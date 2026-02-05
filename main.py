"""
Main Telegram Bot Implementation - FREEMIUM MODEL
"""
from datetime import datetime, timezone  
import os
import logging
import asyncio
from datetime import datetime
from pathlib import Path
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.constants import ParseMode

from database import DatabaseManager
from translations import get_text, get_language_keyboard, TRANSLATIONS
from converters import FileConverter, get_file_extension, get_supported_formats
from subscribe import require_subscription, setup_subscription_handlers
from config import *


# Initialize
db = DatabaseManager()
converter = FileConverter()

async def notify_admin_new_user(context: ContextTypes.DEFAULT_TYPE, user_id: int, username: str, first_name: str, last_name: str):
    """Notify admin about new user registration"""
    try:
        # Get total user count
        total_users_result = db.supabase.table('converter_users').select('user_id', count='exact').execute()
        total_users = total_users_result.count if total_users_result.count else 0
        
        # Format user info
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        username_str = f"@{username}" if username else "No username"
        
        admin_message = (
            "🆕 <b>New User Registered!</b>\n\n"
            f"👤 <b>Name:</b> {full_name or 'No name'}\n"
            f"🔤 <b>Username:</b> {username_str}\n"
            f"🆔 <b>User ID:</b> <code>{user_id}</code>\n\n"
            f"📊 <b>Total Users:</b> {total_users}"
        )
        
        # Send to all notification admins
        for admin_id in NOTIFICATION_ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    parse_mode=ParseMode.HTML
                )
                logger.info(f"✅ Sent new user notification to admin {admin_id}")
            except Exception as e:
                logger.error(f"❌ Failed to send notification to admin {admin_id}: {e}")
    
    except Exception as e:
        logger.error(f"Error in notify_admin_new_user: {e}")


async def get_user_limits(user_id: int) -> dict:
    """Get user's conversion limits based on their tier"""
    is_premium = await db.is_premium_user(user_id)
    
    if is_premium:
        return PREMIUM_TIER_LIMITS
    else:
        return FREE_TIER_LIMITS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Check if user exists in database
    db_user = await db.get_user(user.id)
    
    if not db_user:
        # New user - create in database first
        await db.create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code='en'  # Default language
        )
        logger.info(f"NEW_USER_AUTO_SAVED: User {user.id} auto-saved with default 'en'")
        
        # ⭐ Notify admin about new user
        await notify_admin_new_user(
            context=context,
            user_id=user.id,
            username=user.username or '',
            first_name=user.first_name or '',
            last_name=user.last_name or ''
        )
        
        # Ask for language selection
        await update.message.reply_text(
            "🌍 <b>Please select your language / Пожалуйста, выберите язык / Iltimos, tilni tanlang:</b>",
            reply_markup=get_language_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    # Existing user - check subscription first
    if not await require_subscription(update, context, db_user):
        return

    # ADMIN DASHBOARD CHECK - FIXED TO SHOW FOR ALL ADMINS
    if str(user.id) in NOTIFICATION_ADMIN_IDS:
        # Get admin statistics
        try:
            # Get total users
            total_users_result = db.supabase.table('converter_users').select(
                'user_id', count='exact'
            ).execute()
            total_users = total_users_result.count if total_users_result.count else 0
            
            # Get today's active users
            today = datetime.now(timezone.utc).date().isoformat()
            active_today_result = db.supabase.table('converter_user_stats').select(
                'user_id', count='exact'
            ).eq('last_conversion_date', today).execute()
            todays_active_users = active_today_result.count if active_today_result.count else 0
            
            # Get total processed files
            total_files_result = db.supabase.table('file_conversions').select(
                'id', count='exact'
            ).execute()
            total_processed_files = total_files_result.count if total_files_result.count else 0
            
            # Get successful conversions
            successful_files_result = db.supabase.table('file_conversions').select(
                'id', count='exact'
            ).eq('conversion_status', 'success').execute()
            successful_files = successful_files_result.count if successful_files_result.count else 0
            
            # Calculate success rate
            success_rate = (successful_files / total_processed_files * 100) if total_processed_files > 0 else 0
            
            # Calculate average files per user
            avg_files_per_user = total_processed_files / total_users if total_users > 0 else 0
            
            admin_message = (
                "👑 <b>Admin Dashboard</b>\n\n"
                f"📊 Total Users: <b>{total_users}</b>\n"
                f"👥 Active Users Today: <b>{todays_active_users}</b>\n"
                f"📝 Total Processed Files: <b>{total_processed_files}</b>\n\n"
                "📈 <b>Statistics:</b>\n"
                f"• Average files per user: <b>{avg_files_per_user:.1f}</b>\n"
                f"• Success rate: <b>{success_rate:.1f}%</b>\n"
                f"• Successful conversions: <b>{successful_files}</b>\n\n"
                "🔧 <b>Admin Commands:</b>\n"
                "/stats - Detailed statistics\n"
                "/users - User management\n"
                "/broadcast - Send message to all users"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
                    InlineKeyboardButton("👥 Users", callback_data="admin_users")
                ],
                [
                    InlineKeyboardButton("💰 Payments", callback_data="admin_payments"),
                    InlineKeyboardButton("📝 Conversions", callback_data="admin_conversions")
                ],
                [
                    InlineKeyboardButton("🔄 Use Bot", callback_data="use_bot")
                ]
            ]
            
            await update.message.reply_text(
                admin_message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            return
            
        except Exception as e:
            logger.error(f"Error getting admin stats: {e}")
            # Fall through to regular user flow if error
    
    # Existing user - show category selection with their saved language
    lang = db_user.get('language_code', 'en')
    
    # Check if premium
    is_premium = await db.is_premium_user(user.id)
    
    if is_premium:
        welcome_text = get_text(lang, 'welcome_premium')
    else:
        welcome_text = get_text(lang, 'welcome_free')
    
    category_prompt = get_text(lang, 'select_category')
    
    await update.message.reply_text(
        f"{welcome_text}\n\n{category_prompt}",
        reply_markup=get_category_keyboard(lang),
        parse_mode=ParseMode.HTML
    )


# Add callback handler for "Use Bot" button from admin dashboard
async def use_bot_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin switching to regular bot usage"""
    query = update.callback_query
    await query.answer()
    
    user = await db.get_user(query.from_user.id)
    lang = user.get('language_code', 'en')
    
    is_premium = await db.is_premium_user(query.from_user.id)
    
    if is_premium:
        welcome_text = get_text(lang, 'welcome_premium')
    else:
        welcome_text = get_text(lang, 'welcome_free')
    
    category_prompt = get_text(lang, 'select_category')
    
    await query.edit_message_text(
        f"{welcome_text}\n\n{category_prompt}",
        reply_markup=get_category_keyboard(lang),
        parse_mode=ParseMode.HTML
    )

async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file category selection"""
    query = update.callback_query
    await query.answer()
    
    user = await db.get_user(query.from_user.id)
    lang = user.get('language_code', 'en')
    
    category = query.data.split('_')[1]
    
    # Store selected category
    context.user_data['selected_category'] = category
    
    # Category-specific messages
    category_messages = {
        'pdf': get_text(lang, 'send_pdf'),
        'word': get_text(lang, 'send_word'),
        'image': get_text(lang, 'send_image'),
        'excel': get_text(lang, 'send_excel'),
        'audio': get_text(lang, 'send_audio'),
        'video': get_text(lang, 'send_video'),
        'ppt': get_text(lang, 'send_ppt'),
        'other': get_text(lang, 'send_other')
    }
    
    message = category_messages.get(category, get_text(lang, 'send_file'))
    
    # Add back button
    keyboard = [[InlineKeyboardButton(get_text(lang, 'btn_back'), callback_data='back_to_categories')]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def back_to_categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to categories"""
    query = update.callback_query
    await query.answer()
    
    user = await db.get_user(query.from_user.id)
    lang = user.get('language_code', 'en')
    
    category_prompt = get_text(lang, 'select_category')
    
    await query.edit_message_text(
        category_prompt,
        reply_markup=get_category_keyboard(lang),
        parse_mode=ParseMode.HTML
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.split('_')[1]
    user_id = query.from_user.id
    
    # Update user language
    await db.update_user_language(user_id, lang_code)
    
    # Send welcome message
    is_premium = await db.is_premium_user(user_id)
    
    if is_premium:
        welcome_text = get_text(lang_code, 'welcome_premium')
    else:
        welcome_text = get_text(lang_code, 'welcome_free')
    
    await query.edit_message_text(
        welcome_text,
        parse_mode=ParseMode.HTML
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    help_text = get_text(lang, 'help')
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)


async def formats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /formats command"""
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    formats_text = get_text(lang, 'formats')
    await update.message.reply_text(formats_text, parse_mode=ParseMode.HTML)


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command"""
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    info_text = get_text(lang, 'info')
    await update.message.reply_text(info_text, parse_mode=ParseMode.HTML)


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language command"""
    await update.message.reply_text(
        "🌍 Select your language:",
        reply_markup=get_language_keyboard()
    )


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subscribe command - show upgrade options"""
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    # Check if already premium
    is_premium = await db.is_premium_user(update.effective_user.id)
    
    if is_premium:
        expiry = user.get('subscription_expires_at', '')
        if expiry:
            expiry_date = datetime.fromisoformat(expiry.replace('Z', '+00:00')).strftime('%Y-%m-%d')
        else:
            expiry_date = 'N/A'
        
        stats = await db.get_user_stats(update.effective_user.id)
        conversions_today = stats.get('conversions_today', 0) if stats else 0
        
        text = get_text(lang, 'premium_active',
                       expiry_date=expiry_date,
                       conversions_today=conversions_today)
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    # Show upgrade options for free users
    stats = await db.get_user_stats(update.effective_user.id)
    conversions_today = stats.get('conversions_today', 0) if stats else 0
    
    text = get_text(lang, 'upgrade_to_premium', 
                   card_number=CARD_NUMBER,
                   conversions_today=conversions_today,
                   daily_limit=FREE_TIER_LIMITS['daily_conversions'])
    
    keyboard = [
        [InlineKeyboardButton(
            get_text(lang, 'btn_monthly'),
            callback_data='plan_1'
        )],
        [InlineKeyboardButton(
            get_text(lang, 'btn_quarterly'),
            callback_data='plan_2'
        )],
        [InlineKeyboardButton(
            get_text(lang, 'btn_yearly'),
            callback_data='plan_3'
        )]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


async def plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subscription plan selection"""
    query = update.callback_query
    await query.answer()
    
    plan_id = int(query.data.split('_')[1])
    user_id = query.from_user.id
    
    # Get plan details
    plan = await db.get_plan_by_id(plan_id)
    if not plan:
        return
    
    # Store selected plan in user context
    context.user_data['selected_plan'] = plan_id
    
    user = await db.get_user(user_id)
    lang = user.get('language_code', 'en')
    
    # Show payment sent confirmation to user
    plan_names = {
        1: {'uz': 'Oylik', 'ru': 'Месячный', 'en': 'Monthly'},
        2: {'uz': 'Choraklik', 'ru': 'Квартальный', 'en': 'Quarterly'},
        3: {'uz': 'Yillik', 'ru': 'Годовой', 'en': 'Yearly'}
    }
    
    confirmation_text = {
        'uz': (
            f"✅ <b>To'lov so'rovi yuborildi!</b>\n\n"
            f"📦 Tarif: <b>{plan_names[plan_id]['uz']}</b>\n"
            f"💰 Summa: <b>{int(plan['price']):,} UZS</b>\n\n"
            f"⏳ Admin tasdiqlashini kuting.\n"
            f"📱 Tasdiqlangach sizga xabar beramiz!\n\n"
            f"💳 To'lov qilish uchun:\n"
            f"1️⃣ {int(plan['price']):,} UZS ni kartaga o'tkazing: <code>{CARD_NUMBER}</code>\n"
            f"2️⃣ To'lov chekini adminga yuboring: {ADMIN_USERNAME}\n"
            f"3️⃣ Tasdiqlashni kuting"
        ),
        'ru': (
            f"✅ <b>Запрос на оплату отправлен!</b>\n\n"
            f"📦 Тариф: <b>{plan_names[plan_id]['ru']}</b>\n"
            f"💰 Сумма: <b>{int(plan['price']):,} UZS</b>\n\n"
            f"⏳ Ожидайте подтверждения админа.\n"
            f"📱 Мы уведомим вас после подтверждения!\n\n"
            f"💳 Для оплаты:\n"
            f"1️⃣ Переведите {int(plan['price']):,} UZS на карту: <code>{CARD_NUMBER}</code>\n"
            f"2️⃣ Отправьте чек админу: {ADMIN_USERNAME}\n"
            f"3️⃣ Дождитесь подтверждения"
        ),
        'en': (
            f"✅ <b>Payment request sent!</b>\n\n"
            f"📦 Plan: <b>{plan_names[plan_id]['en']}</b>\n"
            f"💰 Amount: <b>{int(plan['price']):,} UZS</b>\n\n"
            f"⏳ Waiting for admin confirmation.\n"
            f"📱 We'll notify you after confirmation!\n\n"
            f"💳 To pay:\n"
            f"1️⃣ Transfer {int(plan['price']):,} UZS to card: <code>{CARD_NUMBER}</code>\n"
            f"2️⃣ Send receipt to admin: {ADMIN_USERNAME}\n"
            f"3️⃣ Wait for confirmation"
        )
    }
    
    keyboard = [[InlineKeyboardButton(
        get_text(lang, 'send_check') if lang == 'uz' else ("📤 Отправить чек" if lang == 'ru' else "📤 Send receipt"),
        url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"
    )]]
    
    await query.edit_message_text(
        confirmation_text.get(lang, confirmation_text['en']),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    
    # Send payment request to all admins
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_mention = f"@{query.from_user.username}" if query.from_user.username else query.from_user.first_name
    
    admin_text = (
        f"💎 <b>New Premium Subscription Request</b>\n\n"
        f"📅 Time: {timestamp}\n"
        f"👤 User ID: <code>{user_id}</code>\n"
        f"👤 Name: {user_mention}\n"
        f"📦 Plan: <b>{plan_names[plan_id]['en']}</b>\n"
        f"💰 Amount: <b>{int(plan['price']):,} UZS</b>\n"
        f"⏰ Duration: <b>{plan['duration_days']} days</b>\n\n"
        f"⏰ Waiting for payment confirmation..."
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_sub_{user_id}_{plan_id}"
            ),
            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_sub_{user_id}_{plan_id}"
            )
        ]
    ]
    
    for admin_id in NOTIFICATION_ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            logger.info(f"✅ Sent subscription request to admin {admin_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send notification to admin {admin_id}: {e}")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming documents/files - WITH ENHANCED LOGGING"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    logger.info(f"📄 User ID:{user_id} Name:{username} sent a document")
    
    user = await db.get_user(user_id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    # Check if waiting for payment proof
    if context.user_data.get('awaiting_payment'):
        logger.info(f"💳 User ID:{user_id} sent payment proof")
        await handle_payment_proof(update, context)
        return
    
    # Get user limits
    limits = await get_user_limits(user_id)
    is_premium = await db.is_premium_user(user_id)
    
    logger.info(f"👤 User ID:{user_id} - Premium: {is_premium}, Daily limit: {limits['daily_conversions']}")
    
    # Check daily limit
    if await db.check_daily_limit(user_id, limits['daily_conversions']):
        logger.warning(f"⚠️ User ID:{user_id} Name:{username} reached daily limit")
        text = get_text(lang, 'limit_reached_free' if not is_premium else 'limit_reached_premium')
        
        # Show upgrade button for free users
        if not is_premium:
            keyboard = [[InlineKeyboardButton(
                get_text(lang, 'btn_upgrade'),
                callback_data='upgrade_prompt'
            )]]
            await update.message.reply_text(text, 
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    # Get file info
    document = update.message.document
    if not document:
        logger.error(f"❌ User ID:{user_id} - No document in message")
        return
    
    file_name = document.file_name
    file_size = document.file_size
    file_ext = get_file_extension(file_name)
    
    logger.info(f"📁 User ID:{user_id} - File: {file_name}, Size: {file_size} bytes, Type: {file_ext}")
    
    # Check file size limits
    max_size_mb = limits['max_file_size_mb']
    
    if file_size > max_size_mb * 1024 * 1024:
        logger.warning(f"⚠️ User ID:{user_id} Name:{username} - File too large: {file_size/(1024*1024):.2f}MB > {max_size_mb}MB")
        text = get_text(lang, 'file_too_large_free' if not is_premium else 'file_too_large_premium', 
                       max_size=max_size_mb)
        
        # Show upgrade button for free users
        if not is_premium:
            keyboard = [[InlineKeyboardButton(
                get_text(lang, 'btn_upgrade'),
                callback_data='upgrade_prompt'
            )]]
            await update.message.reply_text(text, 
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    # Get supported formats
    supported_formats = get_supported_formats(file_ext)
    
    if not supported_formats:
        logger.warning(f"⚠️ User ID:{user_id} Name:{username} - Unsupported format: {file_ext}")
        text = get_text(lang, 'unsupported_format')
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    logger.info(f"✅ User ID:{user_id} - Supported formats for {file_ext}: {supported_formats}")
    
    # Store file info in context
    context.user_data['file_id'] = document.file_id
    context.user_data['file_name'] = file_name
    context.user_data['file_size'] = file_size
    context.user_data['file_ext'] = file_ext
    
    # Create format selection keyboard
    keyboard = []
    for fmt in supported_formats:
        keyboard.append([
            InlineKeyboardButton(
                f"📄 {fmt.upper()}",
                callback_data=f'convert_{fmt}'
            )
        ])
    
    # Show remaining conversions for free users
    if not is_premium:
        stats = await db.get_user_stats(user_id)
        conversions_today = stats.get('conversions_today', 0) if stats else 0
        remaining = limits['daily_conversions'] - conversions_today
        
        logger.info(f"📊 User ID:{user_id} - Used today: {conversions_today}, Remaining: {remaining}")
        text = get_text(lang, 'select_format_with_limit', remaining=remaining)
    else:
        text = get_text(lang, 'select_format')
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    logger.info(f"✅ Sent format selection to user ID:{user_id} Name:{username}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photos - WITH FREEMIUM RESTRICTIONS"""
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    # Check if waiting for payment proof
    if context.user_data.get('awaiting_payment'):
        await handle_payment_proof(update, context)
        return
    
    # Get user limits
    limits = await get_user_limits(update.effective_user.id)
    is_premium = await db.is_premium_user(update.effective_user.id)
    
    # Check daily limit
    if await db.check_daily_limit(update.effective_user.id, limits['daily_conversions']):
        text = get_text(lang, 'limit_reached_free' if not is_premium else 'limit_reached_premium')
        
        if not is_premium:
            keyboard = [[InlineKeyboardButton(
                get_text(lang, 'btn_upgrade'),
                callback_data='upgrade_prompt'
            )]]
            await update.message.reply_text(text, 
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    # Get largest photo
    photo = update.message.photo[-1]
    file_size = photo.file_size
    
    # Check file size
    max_size_mb = limits['max_file_size_mb']
    if file_size > max_size_mb * 1024 * 1024:
        text = get_text(lang, 'file_too_large_free' if not is_premium else 'file_too_large_premium',
                       max_size=max_size_mb)
        
        if not is_premium:
            keyboard = [[InlineKeyboardButton(
                get_text(lang, 'btn_upgrade'),
                callback_data='upgrade_prompt'
            )]]
            await update.message.reply_text(text, 
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    # Store file info
    context.user_data['file_id'] = photo.file_id
    context.user_data['file_name'] = f'photo_{photo.file_unique_id}.jpg'
    context.user_data['file_size'] = file_size
    context.user_data['file_ext'] = 'jpg'
    
    # Show conversion options
    supported_formats = get_supported_formats('jpg')
    keyboard = []
    for fmt in supported_formats:
        keyboard.append([
            InlineKeyboardButton(
                f"📄 {fmt.upper()}",
                callback_data=f'convert_{fmt}'
            )
        ])
    
    # Show remaining conversions for free users
    if not is_premium:
        stats = await db.get_user_stats(update.effective_user.id)
        conversions_today = stats.get('conversions_today', 0) if stats else 0
        remaining = limits['daily_conversions'] - conversions_today
        
        text = get_text(lang, 'select_format_with_limit', remaining=remaining)
    else:
        text = get_text(lang, 'select_format')
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming audio files - WITH FREEMIUM RESTRICTIONS"""
    logger.info(f"Received AUDIO from user {update.effective_user.id}")
    
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    # Check if waiting for payment proof
    if context.user_data.get('awaiting_payment'):
        await handle_payment_proof(update, context)
        return
    
    # Get user limits
    limits = await get_user_limits(update.effective_user.id)
    is_premium = await db.is_premium_user(update.effective_user.id)
    
    # Check daily limit
    if await db.check_daily_limit(update.effective_user.id, limits['daily_conversions']):
        text = get_text(lang, 'limit_reached_free' if not is_premium else 'limit_reached_premium')
        if not is_premium:
            keyboard = [[InlineKeyboardButton(
                get_text(lang, 'btn_upgrade'),
                callback_data='upgrade_prompt'
            )]]
            await update.message.reply_text(text, 
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    # Get audio info
    audio = update.message.audio
    file_name = audio.file_name or f"audio_{audio.file_unique_id}.mp3"
    file_size = audio.file_size
    file_ext = get_file_extension(file_name)
    
    logger.info(f"Audio details - Name: {file_name}, Size: {file_size}, Ext: {file_ext}")
    
    # Check file size
    max_size_mb = limits['max_file_size_mb']
    if file_size > max_size_mb * 1024 * 1024:
        text = get_text(lang, 'file_too_large_free' if not is_premium else 'file_too_large_premium',
                       max_size=max_size_mb)
        if not is_premium:
            keyboard = [[InlineKeyboardButton(
                get_text(lang, 'btn_upgrade'),
                callback_data='upgrade_prompt'
            )]]
            await update.message.reply_text(text, 
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    # Store file info
    context.user_data['file_id'] = audio.file_id
    context.user_data['file_name'] = file_name
    context.user_data['file_size'] = file_size
    context.user_data['file_ext'] = file_ext
    
    # Show conversion options
    supported_formats = get_supported_formats(file_ext)
    logger.info(f"Supported formats for {file_ext}: {supported_formats}")
    
    keyboard = []
    for fmt in supported_formats:
        keyboard.append([
            InlineKeyboardButton(
                f"🎵 {fmt.upper()}",
                callback_data=f'convert_{fmt}'
            )
        ])
    
    # Show remaining conversions for free users
    if not is_premium:
        stats = await db.get_user_stats(update.effective_user.id)
        conversions_today = stats.get('conversions_today', 0) if stats else 0
        remaining = limits['daily_conversions'] - conversions_today
        text = get_text(lang, 'select_format_with_limit', remaining=remaining)
    else:
        text = get_text(lang, 'select_format')
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming voice messages (OGG format)"""
    logger.info(f"Received VOICE from user {update.effective_user.id}")
    
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    # Check if waiting for payment proof
    if context.user_data.get('awaiting_payment'):
        await handle_payment_proof(update, context)
        return
    
    # Get user limits
    limits = await get_user_limits(update.effective_user.id)
    is_premium = await db.is_premium_user(update.effective_user.id)
    
    # Check daily limit
    if await db.check_daily_limit(update.effective_user.id, limits['daily_conversions']):
        text = get_text(lang, 'limit_reached_free' if not is_premium else 'limit_reached_premium')
        if not is_premium:
            keyboard = [[InlineKeyboardButton(
                get_text(lang, 'btn_upgrade'),
                callback_data='upgrade_prompt'
            )]]
            await update.message.reply_text(text, 
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    # Get voice info
    voice = update.message.voice
    file_name = f"voice_{voice.file_unique_id}.ogg"
    file_size = voice.file_size
    file_ext = 'ogg'
    
    logger.info(f"Voice details - Name: {file_name}, Size: {file_size}, Ext: {file_ext}")
    
    # Check file size
    max_size_mb = limits['max_file_size_mb']
    if file_size > max_size_mb * 1024 * 1024:
        text = get_text(lang, 'file_too_large_free' if not is_premium else 'file_too_large_premium',
                       max_size=max_size_mb)
        if not is_premium:
            keyboard = [[InlineKeyboardButton(
                get_text(lang, 'btn_upgrade'),
                callback_data='upgrade_prompt'
            )]]
            await update.message.reply_text(text, 
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    # Store file info
    context.user_data['file_id'] = voice.file_id
    context.user_data['file_name'] = file_name
    context.user_data['file_size'] = file_size
    context.user_data['file_ext'] = file_ext
    
    # Show conversion options
    supported_formats = get_supported_formats(file_ext)
    logger.info(f"Supported formats for {file_ext}: {supported_formats}")
    
    keyboard = []
    for fmt in supported_formats:
        keyboard.append([
            InlineKeyboardButton(
                f"🎵 {fmt.upper()}",
                callback_data=f'convert_{fmt}'
            )
        ])
    
    # Show remaining conversions for free users
    if not is_premium:
        stats = await db.get_user_stats(update.effective_user.id)
        conversions_today = stats.get('conversions_today', 0) if stats else 0
        remaining = limits['daily_conversions'] - conversions_today
        text = get_text(lang, 'select_format_with_limit', remaining=remaining)
    else:
        text = get_text(lang, 'select_format')
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming video files - WITH FREEMIUM RESTRICTIONS"""
    logger.info(f"Received VIDEO from user {update.effective_user.id}")
    
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    # Check if waiting for payment proof
    if context.user_data.get('awaiting_payment'):
        await handle_payment_proof(update, context)
        return
    
    # Get user limits
    limits = await get_user_limits(update.effective_user.id)
    is_premium = await db.is_premium_user(update.effective_user.id)
    
    # Check daily limit
    if await db.check_daily_limit(update.effective_user.id, limits['daily_conversions']):
        text = get_text(lang, 'limit_reached_free' if not is_premium else 'limit_reached_premium')
        if not is_premium:
            keyboard = [[InlineKeyboardButton(
                get_text(lang, 'btn_upgrade'),
                callback_data='upgrade_prompt'
            )]]
            await update.message.reply_text(text, 
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    # Get video info
    video = update.message.video
    file_name = video.file_name or f"video_{video.file_unique_id}.mp4"
    file_size = video.file_size
    file_ext = get_file_extension(file_name)
    
    logger.info(f"Video details - Name: {file_name}, Size: {file_size}, Ext: {file_ext}")
    
    # Check file size
    max_size_mb = limits['max_file_size_mb']
    if file_size > max_size_mb * 1024 * 1024:
        text = get_text(lang, 'file_too_large_free' if not is_premium else 'file_too_large_premium',
                       max_size=max_size_mb)
        if not is_premium:
            keyboard = [[InlineKeyboardButton(
                get_text(lang, 'btn_upgrade'),
                callback_data='upgrade_prompt'
            )]]
            await update.message.reply_text(text, 
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    # Store file info
    context.user_data['file_id'] = video.file_id
    context.user_data['file_name'] = file_name
    context.user_data['file_size'] = file_size
    context.user_data['file_ext'] = file_ext
    
    # Show conversion options
    supported_formats = get_supported_formats(file_ext)
    logger.info(f"Supported formats for {file_ext}: {supported_formats}")
    
    keyboard = []
    for fmt in supported_formats:
        keyboard.append([
            InlineKeyboardButton(
                f"🎬 {fmt.upper()}",
                callback_data=f'convert_{fmt}'
            )
        ])
    
    # Show remaining conversions for free users
    if not is_premium:
        stats = await db.get_user_stats(update.effective_user.id)
        conversions_today = stats.get('conversions_today', 0) if stats else 0
        remaining = limits['daily_conversions'] - conversions_today
        text = get_text(lang, 'select_format_with_limit', remaining=remaining)
    else:
        text = get_text(lang, 'select_format')
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

# Add general message logger to catch all unhandled message types
async def log_unhandled_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log unhandled message types for debugging"""
    message = update.message
    logger.warning(f"UNHANDLED message type from user {update.effective_user.id}:")
    logger.warning(f"  - Has text: {message.text is not None}")
    logger.warning(f"  - Has document: {message.document is not None}")
    logger.warning(f"  - Has photo: {message.photo is not None}")
    logger.warning(f"  - Has audio: {message.audio is not None}")
    logger.warning(f"  - Has voice: {message.voice is not None}")
    logger.warning(f"  - Has video: {message.video is not None}")
    logger.warning(f"  - Has video_note: {message.video_note is not None}")
    logger.warning(f"  - Has animation: {message.animation is not None}")
    logger.warning(f"  - Has sticker: {message.sticker is not None}")


async def upgrade_prompt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle upgrade prompt button"""
    query = update.callback_query
    await query.answer()
    
    user = await db.get_user(query.from_user.id)
    lang = user.get('language_code', 'en')
    
    stats = await db.get_user_stats(query.from_user.id)
    conversions_today = stats.get('conversions_today', 0) if stats else 0
    
    text = get_text(lang, 'upgrade_to_premium',
                   card_number=CARD_NUMBER,
                   conversions_today=conversions_today,
                   daily_limit=FREE_TIER_LIMITS['daily_conversions'])
    
    keyboard = [
        [InlineKeyboardButton(
            get_text(lang, 'btn_monthly'),
            callback_data='plan_1'
        )],
        [InlineKeyboardButton(
            get_text(lang, 'btn_quarterly'),
            callback_data='plan_2'
        )],
        [InlineKeyboardButton(
            get_text(lang, 'btn_yearly'),
            callback_data='plan_3'
        )]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


async def convert_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle format conversion - WITH ENHANCED LOGGING"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name
    
    user = await db.get_user(user_id)
    lang = user.get('language_code', 'en')
    
    target_format = query.data.split('_')[1]
    
    # Get file info from context
    file_id = context.user_data.get('file_id')
    file_name = context.user_data.get('file_name')
    file_size = context.user_data.get('file_size')
    file_ext = context.user_data.get('file_ext')
    
    logger.info(f"🔄 User ID:{user_id} Name:{username} started conversion: {file_ext} -> {target_format}")
    
    if not file_id:
        logger.error(f"❌ User ID:{user_id} - No file_id in context")
        return
    
    # Send processing message
    text = get_text(lang, 'converting', format=target_format.upper())
    processing_msg = await query.edit_message_text(text, parse_mode=ParseMode.HTML)
    logger.info(f"📤 Sent processing message to user ID:{user_id}")
    
    try:
        start_time = time.time()
        
        # Download file
        logger.info(f"⬇️ Downloading file for user ID:{user_id} - {file_name} ({file_size} bytes)")
        file = await context.bot.get_file(file_id)
        input_path = f'/tmp/{file_id}_{file_name}'
        await file.download_to_drive(input_path)
        logger.info(f"✅ Download complete for user ID:{user_id} - Path: {input_path}")
        
        # Convert file
        logger.info(f"🔧 Starting conversion for user ID:{user_id} - {file_ext} to {target_format}")
        output_path = converter.convert(input_path, target_format)
        
        if not output_path or not os.path.exists(output_path):
            logger.error(f"❌ Conversion failed for user ID:{user_id} - Output file not created")
            raise Exception("Conversion failed")
        
        processing_time = time.time() - start_time
        output_size = os.path.getsize(output_path)
        logger.info(f"✅ Conversion successful for user ID:{user_id} - Time: {processing_time:.2f}s, Size: {output_size} bytes")
        
        # Create proper output filename (keep original name, change extension)
        original_name_without_ext = Path(file_name).stem
        output_filename = f"{original_name_without_ext}.{target_format}"
        
        # Send converted file
        logger.info(f"📤 Sending converted file to user ID:{user_id} - {output_filename}")
        text = get_text(lang, 'conversion_success')
        with open(output_path, 'rb') as output_file:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=output_file,
                filename=output_filename,
                caption=text,
                parse_mode=ParseMode.HTML
            )
        logger.info(f"✅ File sent successfully to user ID:{user_id} Name:{username}")
        
        # Log conversion
        await db.log_conversion(
            user_id=user_id,
            original_filename=file_name,
            original_format=file_ext,
            target_format=target_format,
            file_size=file_size,
            status='success',
            processing_time=processing_time
        )
        logger.info(f"📊 Logged successful conversion for user ID:{user_id}")
        
        # Clean up
        try:
            os.remove(input_path)
            os.remove(output_path)
            logger.info(f"🗑️ Cleaned up temp files for user ID:{user_id}")
        except Exception as cleanup_error:
            logger.warning(f"⚠️ Cleanup error for user ID:{user_id}: {cleanup_error}")
        
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"❌ Conversion error for user ID:{user_id} Name:{username} - Error: {e}", exc_info=True)
        text = get_text(lang, 'conversion_failed', error=str(e))
        await processing_msg.edit_text(text, parse_mode=ParseMode.HTML)
        
        # Log failed conversion
        await db.log_conversion(
            user_id=user_id,
            original_filename=file_name,
            original_format=file_ext,
            target_format=target_format,
            file_size=file_size,
            status='failed',
            error_message=str(e)
        )
        logger.info(f"📊 Logged failed conversion for user ID:{user_id}")


async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment proof screenshot"""
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language_code', 'en')
    
    selected_plan = context.user_data.get('selected_plan')
    if not selected_plan:
        return
    
    # Get file ID
    file_id = None
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.document:
        file_id = update.message.document.file_id
    
    if not file_id:
        return
    
    # Get plan details
    plan = await db.get_plan_by_id(selected_plan)
    
    # Create payment record
    payment_id = await db.create_payment(
        user_id=update.effective_user.id,
        plan_id=selected_plan,
        amount=plan['price'],
        file_id=file_id
    )
    
    # Notify user
    text = get_text(lang, 'payment_proof_sent')
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    # Notify admins
    plan_name = ['Monthly', 'Quarterly', 'Yearly'][selected_plan - 1]
    user_mention = f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.first_name
    
    admin_text = get_text('en', 'new_payment',
                         user=user_mention,
                         plan=plan_name,
                         amount=int(plan['price']),
                         user_id=update.effective_user.id)
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f'approve_{payment_id}'),
            InlineKeyboardButton("❌ Reject", callback_data=f'reject_{payment_id}')
        ]
    ]
    
    for admin_id in NOTIFICATION_ADMIN_IDS:
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=admin_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error notifying admin {admin_id}: {e}")
    
    # Clear context
    context.user_data['awaiting_payment'] = False
    context.user_data['selected_plan'] = None


async def approve_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment approval by admin"""
    query = update.callback_query
    await query.answer()
    
    if str(query.from_user.id) not in NOTIFICATION_ADMIN_IDS:
        await query.answer("You are not authorized", show_alert=True)
        return
    
    payment_id = int(query.data.split('_')[1])
    
    # Approve payment
    success = await db.approve_payment(payment_id, query.from_user.id)
    
    if success:
        # Get payment info
        payment = await db.get_payment(payment_id)
        user_id = payment['user_id']
        
        # Get user language
        user = await db.get_user(user_id)
        lang = user.get('language_code', 'en')
        
        # Notify user
        text = get_text(lang, 'payment_approved')
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n✅ APPROVED",
            parse_mode=ParseMode.HTML
        )


async def reject_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment rejection by admin"""
    query = update.callback_query
    await query.answer()
    
    if str(query.from_user.id) not in NOTIFICATION_ADMIN_IDS:
        await query.answer("You are not authorized", show_alert=True)
        return
    
    payment_id = int(query.data.split('_')[1])
    
    # Reject payment
    success = await db.reject_payment(payment_id, query.from_user.id, "Rejected by admin")
    
    if success:
        # Get payment info
        payment = await db.get_payment(payment_id)
        user_id = payment['user_id']
        
        # Get user language
        user = await db.get_user(user_id)
        lang = user.get('language_code', 'en')
        
        # Notify user
        text = get_text(lang, 'payment_rejected', reason="Please contact support")
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n❌ REJECTED",
            parse_mode=ParseMode.HTML
        )



def get_category_keyboard(lang: str):
    """Get file category selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📄 PDF", callback_data='category_pdf'),
            InlineKeyboardButton("📝 Word", callback_data='category_word')
        ],
        [
            InlineKeyboardButton("🖼 Images", callback_data='category_image'),
            InlineKeyboardButton("📊 Excel", callback_data='category_excel')
        ],
        [
            InlineKeyboardButton("🎵 Audio", callback_data='category_audio'),
            InlineKeyboardButton("🎬 Video", callback_data='category_video')
        ],
        [
            InlineKeyboardButton("📑 PowerPoint", callback_data='category_ppt'),
            InlineKeyboardButton("📦 Other", callback_data='category_other')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def main():
    """Start the bot"""
    # Import admin and broadcast modules
    from admin import (
        stats_command,
        users_command,
        admin_stats_callback,
        admin_back_callback, admin_users_callback,admin_conversions_callback, admin_payments_callback, admin_premium_users_callback
    )
    from broadcast import BroadcastManager
    from balance import handle_custom_amount, topup_balance_command, topup_callback, back_to_topup_callback
    
    # Initialize broadcast manager
    broadcast_manager = BroadcastManager(db)
    
    application = Application.builder().token(BOT_TOKEN).build()
    setup_subscription_handlers(application)

    # ============ EXISTING HANDLERS ============
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("formats", formats_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("language", language_command))
    
    # ============ NEW ADMIN HANDLERS ============
    # Admin commands
    application.add_handler(CommandHandler(
        "stats", 
        lambda u, c: stats_command(u, c, db, NOTIFICATION_ADMIN_IDS)
    ))
    application.add_handler(CommandHandler(
        "users", 
        lambda u, c: users_command(u, c, db, NOTIFICATION_ADMIN_IDS)
    ))
    application.add_handler(CommandHandler(
        "broadcast", 
        lambda u, c: broadcast_manager.start_broadcast(u, c, NOTIFICATION_ADMIN_IDS)
    ))
    
    # ============ EXISTING CALLBACKS ============
    application.add_handler(CallbackQueryHandler(language_callback, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(plan_callback, pattern='^plan_'))
    application.add_handler(CallbackQueryHandler(convert_callback, pattern='^convert_'))
    application.add_handler(CallbackQueryHandler(upgrade_prompt_callback, pattern='^upgrade_prompt$'))
    application.add_handler(CallbackQueryHandler(approve_payment_callback, pattern='^approve_'))
    application.add_handler(CallbackQueryHandler(reject_payment_callback, pattern='^reject_'))
    application.add_handler(CallbackQueryHandler(category_callback, pattern='^category_'))
    application.add_handler(CallbackQueryHandler(back_to_categories_callback, pattern='^back_to_categories$'))
    application.add_handler(CallbackQueryHandler(use_bot_callback, pattern='^use_bot$'))
    application.add_handler(CallbackQueryHandler(topup_callback, pattern='^topup_'))
    application.add_handler(CallbackQueryHandler(back_to_topup_callback, pattern='^back_to_topup$'))
    
    # ============ ADMIN CALLBACKS - COMPLETE LIST ============
    application.add_handler(CallbackQueryHandler(
        lambda u, c: admin_stats_callback(u, c, db),
        pattern='^admin_stats$'
    ))
    application.add_handler(CallbackQueryHandler(
        lambda u, c: admin_back_callback(u, c, db),
        pattern='^admin_back$'
    ))
    application.add_handler(CallbackQueryHandler(
        lambda u, c: admin_users_callback(u, c, db),
        pattern='^admin_users$'
    ))
    application.add_handler(CallbackQueryHandler(
        lambda u, c: admin_payments_callback(u, c, db),
        pattern='^admin_payments$'
    ))
    application.add_handler(CallbackQueryHandler(
        lambda u, c: admin_conversions_callback(u, c, db),
        pattern='^admin_conversions$'
    ))
    application.add_handler(CallbackQueryHandler(
        lambda u, c: admin_premium_users_callback(u, c, db),
        pattern='^admin_premium_users$'
    ))
    
    # Broadcast callbacks
    application.add_handler(CallbackQueryHandler(
        broadcast_manager.handle_language_selection,
        pattern='^broadcast_lang_'
    ))
    application.add_handler(CallbackQueryHandler(
        broadcast_manager.confirm_broadcast,
        pattern='^broadcast_confirm$'
    ))
    application.add_handler(CallbackQueryHandler(
        broadcast_manager.cancel_broadcast,
        pattern='^broadcast_cancel$'
    ))
    
    # ============ MESSAGE HANDLERS - UPDATE ORDER ============
    # Broadcast message handler (MUST be before others)
    async def check_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get('awaiting_broadcast_message'):
            await broadcast_manager.handle_broadcast_message(update, context)
            return
        # Otherwise, handle as custom amount
        await handle_custom_amount(update, context)
    
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        check_broadcast_message
    ))
    
    # Media handlers for broadcast
    async def handle_broadcast_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get('awaiting_broadcast_message'):
            await broadcast_manager.handle_broadcast_message(update, context)
            return
        # Otherwise, handle normally
        if update.message.photo:
            await handle_photo(update, context)
        elif update.message.video:
            await handle_video(update, context)
        elif update.message.document:
            await handle_document(update, context)
    
    # File handlers
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.VIDEO, handle_broadcast_media))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_broadcast_media))
    application.add_handler(MessageHandler(filters.PHOTO, handle_broadcast_media))
    
    # Catch-all for debugging
    application.add_handler(MessageHandler(
        ~filters.COMMAND & ~filters.AUDIO & ~filters.VOICE & ~filters.VIDEO & 
        ~filters.Document.ALL & ~filters.PHOTO & ~filters.TEXT,
        log_unhandled_message
    ))

    # Start bot
    logger.info("🚀 Bot started with ADMIN + BROADCAST system")
    logger.info(f"👥 Admin IDs: {NOTIFICATION_ADMIN_IDS}")
    application.run_polling()

if __name__ == "__main__":
    main()