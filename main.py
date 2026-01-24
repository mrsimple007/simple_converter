"""
Main Telegram Bot Implementation - FREEMIUM MODEL
"""

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

# Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CARD_NUMBER = "4073 4200 3711 6443"
ADMIN_CHAT_ID = "8437026582"
NOTIFICATION_ADMIN_IDS = ["8437026582"]

# FREEMIUM LIMITS
FREE_TIER_LIMITS = {
    'daily_conversions': 10,  # 10 conversions per day for free users
    'max_file_size_mb': 25,   # 25 MB max file size
}

PREMIUM_TIER_LIMITS = {
    'daily_conversions': -1,  # Unlimited
    'max_file_size_mb': 500,  # 500 MB max file size
}

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize
db = DatabaseManager()
converter = FileConverter()


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
        # New user - ask for language
        await db.create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        await update.message.reply_text(
            "🌍 <b>Please select your language / Пожалуйста, выберите язык / Iltimos, tilni tanlang:</b>",
            reply_markup=get_language_keyboard(),
            parse_mode=ParseMode.HTML
        )
    else:
        # Existing user - show category selection
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
    context.user_data['awaiting_payment'] = True
    
    user = await db.get_user(user_id)
    lang = user.get('language_code', 'en')
    
    text = get_text(lang, 'payment_instructions',
                   amount=int(plan['price']),
                   card_number=CARD_NUMBER)
    
    await query.edit_message_text(text, parse_mode=ParseMode.HTML)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming documents/files - WITH FREEMIUM RESTRICTIONS"""
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
        return
    
    file_name = document.file_name
    file_size = document.file_size
    file_ext = get_file_extension(file_name)
    
    # Check file size limits
    max_size_mb = limits['max_file_size_mb']
    
    if file_size > max_size_mb * 1024 * 1024:
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
        text = get_text(lang, 'unsupported_format')
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
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
    """Handle format conversion"""
    query = update.callback_query
    await query.answer()
    
    user = await db.get_user(query.from_user.id)
    lang = user.get('language_code', 'en')
    
    target_format = query.data.split('_')[1]
    
    # Get file info from context
    file_id = context.user_data.get('file_id')
    file_name = context.user_data.get('file_name')
    file_size = context.user_data.get('file_size')
    file_ext = context.user_data.get('file_ext')
    
    if not file_id:
        return
    
    # Send processing message
    text = get_text(lang, 'converting', format=target_format.upper())
    processing_msg = await query.edit_message_text(text, parse_mode=ParseMode.HTML)
    
    try:
        start_time = time.time()
        
        # Download file
        file = await context.bot.get_file(file_id)
        input_path = f'/tmp/{file_id}_{file_name}'
        await file.download_to_drive(input_path)
        
        # Convert file
        output_path = converter.convert(input_path, target_format)
        
        if not output_path or not os.path.exists(output_path):
            raise Exception("Conversion failed")
        
        processing_time = time.time() - start_time
        
        # Create proper output filename (keep original name, change extension)
        original_name_without_ext = Path(file_name).stem
        output_filename = f"{original_name_without_ext}.{target_format}"
        
        # Send converted file
        text = get_text(lang, 'conversion_success')
        with open(output_path, 'rb') as output_file:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=output_file,
                filename=output_filename,  # Use proper filename
                caption=text,
                parse_mode=ParseMode.HTML
            )
        
        # Log conversion
        await db.log_conversion(
            user_id=query.from_user.id,
            original_filename=file_name,
            original_format=file_ext,
            target_format=target_format,
            file_size=file_size,
            status='success',
            processing_time=processing_time
        )
        
        # Clean up
        try:
            os.remove(input_path)
            os.remove(output_path)
        except:
            pass
        
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        text = get_text(lang, 'conversion_failed', error=str(e))
        await processing_msg.edit_text(text, parse_mode=ParseMode.HTML)
        
        # Log failed conversion
        await db.log_conversion(
            user_id=query.from_user.id,
            original_filename=file_name,
            original_format=file_ext,
            target_format=target_format,
            file_size=file_size,
            status='failed',
            error_message=str(e)
        )


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
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("formats", formats_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("language", language_command))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(language_callback, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(plan_callback, pattern='^plan_'))
    application.add_handler(CallbackQueryHandler(convert_callback, pattern='^convert_'))
    application.add_handler(CallbackQueryHandler(upgrade_prompt_callback, pattern='^upgrade_prompt$'))
    application.add_handler(CallbackQueryHandler(approve_payment_callback, pattern='^approve_'))
    application.add_handler(CallbackQueryHandler(reject_payment_callback, pattern='^reject_'))
    application.add_handler(CallbackQueryHandler(category_callback, pattern='^category_'))

    # Message handlers
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(back_to_categories_callback, pattern='^back_to_categories$'))

    # Start bot
    logger.info("🚀 Bot started with FREEMIUM model")
    logger.info(f"📊 Free tier: {FREE_TIER_LIMITS['daily_conversions']} conversions/day, {FREE_TIER_LIMITS['max_file_size_mb']}MB max")
    logger.info(f"💎 Premium tier: Unlimited conversions, {PREMIUM_TIER_LIMITS['max_file_size_mb']}MB max")
    application.run_polling()


if __name__ == "__main__":
    main()