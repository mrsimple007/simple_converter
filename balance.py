"""
Balance top-up handler with multi-language support
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

# Import from main bot file
from main import CARD_NUMBER, ADMIN_USERNAME, NOTIFICATION_ADMIN_IDS, db

# Balance amount options (in kopecks for precision)
BALANCE_AMOUNTS = {
    "10k": 10000,
    "25k": 25000,
    "50k": 50000,
    "100k": 100000,
}

# Translations
BALANCE_TRANSLATIONS = {
    "uz": {
        "topup_title": "💰 <b>Balansni to'ldirish</b>",
        "select_amount": "Summani tanlang:",
        "custom_amount": "🔢 Boshqa summa",
        'payment_approved': "✅ <b>To'lov tasdiqlandi!</b>\n\nSizning balansingiz muvaffaqiyatli to'ldirildi.",
        'payment_rejected': "❌ <b>To'lov rad etildi!</b>\n\n Iltimos, agar xatolik bo'lsa {ADMIN_USERNAME} bilan bog'laning.",
        "back": "« Orqaga",
        "payment_instructions": (
            "💳 <b>To'lov ma'lumotlari</b>\n\n"
            "💰 Summa: <b>{amount} UZS</b>\n"
            "💳 Karta: <code>{card_number}</code>\n\n"
            "📋 <b>To'lov qilish uchun:</b>\n"
            "1️⃣ Yuqoridagi summani kartaga o'tkazing\n"
            "2️⃣ To'lov chekini adminga yuboring: {admin_username}\n"
            "3️⃣ Tasdiqlashni kuting (odatda 5-10 daqiqa)\n\n"
            "⚠️ Chekni 30 daqiqa ichida yuboring!"
        ),
        "send_check": "📤 Chekni yuborish",
        "payment_sent": (
            "✅ <b>To'lov so'rovi yuborildi!</b>\n\n"
            "💰 Summa: <b>{amount} UZS</b>\n\n"
            "⏳ Admin tasdiqlashini kuting.\n"
            "📱 Tasdiqlangach sizga xabar beramiz!"
        ),
        "enter_custom_amount": (
            "🔢 <b>O'z summangizni kiriting</b>\n\n"
            "Minimum: 5,000 UZS\n"
            "Maksimum: 10,000,000 UZS\n\n"
            "Summani faqat raqamlarda yuboring:"
        ),
        "invalid_amount": "❌ Noto'g'ri summa. Iltimos, 5000 dan 10000000 gacha bo'lgan raqam kiriting.",
    },
    "ru": {
        "topup_title": "💰 <b>Пополнение баланса</b>",
        "select_amount": "Выберите сумму:",
        "custom_amount": "🔢 Другая сумма",
        "payment_approved": "✅ <b>Платеж подтвержден!</b>\n\nВаш баланс успешно пополнен.",
        "payment_rejected": "❌ <b>Платеж отклонен!</b>\n\n Пожалуйста, свяжитесь с поддержкой {ADMIN_USERNAME}, если это ошибка.",
        "back": "« Назад",
        "payment_instructions": (
            "💳 <b>Платежная информация</b>\n\n"
            "💰 Сумма: <b>{amount} UZS</b>\n"
            "💳 Карта: <code>{card_number}</code>\n\n"
            "📋 <b>Для оплаты:</b>\n"
            "1️⃣ Переведите указанную сумму на карту\n"
            "2️⃣ Отправьте чек админу: {admin_username}\n"
            "3️⃣ Дождитесь подтверждения (обычно 5-10 минут)\n\n"
            "⚠️ Отправьте чек в течение 30 минут!"
        ),
        "send_check": "📤 Отправить чек",
        "payment_sent": (
            "✅ <b>Запрос на оплату отправлен!</b>\n\n"
            "💰 Сумма: <b>{amount} UZS</b>\n\n"
            "⏳ Ожидайте подтверждения админа.\n"
            "📱 Мы уведомим вас после подтверждения!"
        ),
        "enter_custom_amount": (
            "🔢 <b>Введите свою сумму</b>\n\n"
            "Минимум: 5,000 UZS\n"
            "Максимум: 10,000,000 UZS\n\n"
            "Отправьте сумму только цифрами:"
        ),
        "invalid_amount": "❌ Неверная сумма. Пожалуйста, введите число от 5000 до 10000000.",
    },
    "en": {
        "topup_title": "💰 <b>Top up Balance</b>",
        "select_amount": "Select amount:",
        "custom_amount": "🔢 Custom amount",
        'payment_approved': "✅ <b>Payment Approved!</b>\n\nYour balance has been successfully topped up.",
        'payment_rejected': "❌ <b>Payment Rejected!</b>\n\n Please contact support {ADMIN_USERNAME} if this is an error.",
        "back": "« Back",
        "payment_instructions": (
            "💳 <b>Payment Information</b>\n\n"
            "💰 Amount: <b>{amount} UZS</b>\n"
            "💳 Card: <code>{card_number}</code>\n\n"
            "📋 <b>To pay:</b>\n"
            "1️⃣ Transfer the amount to the card\n"
            "2️⃣ Send receipt to admin: {admin_username}\n"
            "3️⃣ Wait for confirmation (usually 5-10 minutes)\n\n"
            "⚠️ Send receipt within 30 minutes!"
        ),
        "send_check": "📤 Send receipt",
        "payment_sent": (
            "✅ <b>Payment request sent!</b>\n\n"
            "💰 Amount: <b>{amount} UZS</b>\n\n"
            "⏳ Waiting for admin confirmation.\n"
            "📱 We'll notify you after confirmation!"
        ),
        "enter_custom_amount": (
            "🔢 <b>Enter your amount</b>\n\n"
            "Minimum: 5,000 UZS\n"
            "Maximum: 10,000,000 UZS\n\n"
            "Send amount in numbers only:"
        ),
        "invalid_amount": "❌ Invalid amount. Please enter a number between 5000 and 10000000.",
    }
}


async def topup_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /topup command - show balance top-up options"""
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    text = BALANCE_TRANSLATIONS[lang]["topup_title"] + "\n\n"
    text += BALANCE_TRANSLATIONS[lang]["select_amount"]
    
    keyboard = [
        [
            InlineKeyboardButton("10,000 UZS", callback_data="topup_10k"),
            InlineKeyboardButton("25,000 UZS", callback_data="topup_25k"),
        ],
        [
            InlineKeyboardButton("50,000 UZS", callback_data="topup_50k"),
            InlineKeyboardButton("100,000 UZS", callback_data="topup_100k"),
        ],
        [
            InlineKeyboardButton(
                BALANCE_TRANSLATIONS[lang]["custom_amount"],
                callback_data="topup_custom"
            )
        ]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


async def topup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle balance top-up amount selection"""
    query = update.callback_query
    await query.answer()
    
    user = await db.get_user(query.from_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    amount_key = query.data.split('_')[1]
    
    if amount_key == "custom":
        # Ask for custom amount
        text = BALANCE_TRANSLATIONS[lang]["enter_custom_amount"]
        context.user_data['awaiting_custom_amount'] = True
        
        keyboard = [[InlineKeyboardButton(
            BALANCE_TRANSLATIONS[lang]["back"],
            callback_data="back_to_topup"
        )]]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Standard amount selected
    if amount_key in BALANCE_AMOUNTS:
        amount_uzs = BALANCE_AMOUNTS[amount_key]
        await process_topup_payment(query, context, amount_uzs, lang)


async def handle_custom_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom amount input"""
    if not context.user_data.get('awaiting_custom_amount'):
        return
    
    user = await db.get_user(update.effective_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    try:
        amount = int(update.message.text.strip())
        
        if amount < 5000 or amount > 10000000:
            await update.message.reply_text(
                BALANCE_TRANSLATIONS[lang]["invalid_amount"],
                parse_mode=ParseMode.HTML
            )
            return
        
        context.user_data['awaiting_custom_amount'] = False
        
        # Create a fake query object for consistency
        class FakeQuery:
            def __init__(self, user, message):
                self.from_user = user
                self.message = message
            async def answer(self): pass
            async def edit_message_text(self, *args, **kwargs):
                await self.message.reply_text(*args, **kwargs)
        
        fake_query = FakeQuery(update.effective_user, update.message)
        await process_topup_payment(fake_query, context, amount, lang)
        
    except ValueError:
        await update.message.reply_text(
            BALANCE_TRANSLATIONS[lang]["invalid_amount"],
            parse_mode=ParseMode.HTML
        )


async def process_topup_payment(query, context: ContextTypes.DEFAULT_TYPE, amount_uzs: int, lang: str):
    """Process the payment request and notify admins"""
    
    # Show payment instructions to user
    text = BALANCE_TRANSLATIONS[lang]["payment_instructions"].format(
        amount=f"{amount_uzs:,}",
        card_number=CARD_NUMBER,
        admin_username=ADMIN_USERNAME
    )
    
    keyboard = [
        [InlineKeyboardButton(
            BALANCE_TRANSLATIONS[lang]["send_check"],
            url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"
        )]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    
    # Send confirmation to user
    confirmation_text = BALANCE_TRANSLATIONS[lang]["payment_sent"].format(
        amount=f"{amount_uzs:,}"
    )
    
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=confirmation_text,
        parse_mode=ParseMode.HTML
    )
    
    # Send payment request to all admins
    await send_payment_request_to_admins(
        context=context,
        user_id=query.from_user.id,
        user_name=query.from_user.first_name or "User",
        username=query.from_user.username,
        amount_uzs=amount_uzs
    )


async def send_payment_request_to_admins(context: ContextTypes.DEFAULT_TYPE, 
                                        user_id: int, user_name: str,
                                        username: str, amount_uzs: int):
    """Send payment request notification to all admins"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    admin_text = (
        f"💳 <b>New Payment Request</b>\n\n"
        f"📅 Time: {timestamp}\n"
        f"👤 User ID: <code>{user_id}</code>\n"
        f"👤 Name: {user_name}\n"
    )
    
    if username:
        admin_text += f"👤 Username: @{username}\n"
    
    admin_text += (
        f"💰 Amount: <b>{amount_uzs:,} UZS</b>\n"
        f"🏷️ Type: Balance Top-up\n\n"
        f"⏰ Waiting for payment confirmation..."
    )
    
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_{user_id}_{amount_uzs}"
            ),
            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{user_id}_{amount_uzs}"
            )
        ]
    ]
    
    # Store payment info for admin actions
    payment_key = f"payment_{user_id}_{amount_uzs}"
    context.bot_data[payment_key] = {
        'user_id': user_id,
        'amount': amount_uzs,
        'timestamp': timestamp,
        'user_name': user_name,
        'username': username
    }
    
    # Send to all notification admins
    for admin_id in NOTIFICATION_ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
            logger.info(f"✅ Sent payment notification to admin {admin_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send payment notification to admin {admin_id}: {e}")

async def approve_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment approval by admin"""
    query = update.callback_query
    await query.answer()
    
    if str(query.from_user.id) not in NOTIFICATION_ADMIN_IDS:
        await query.answer("You are not authorized", show_alert=True)
        return
    
    # Check if it's subscription or balance payment
    if query.data.startswith('approve_sub_'):
        # Subscription approval
        parts = query.data.split('_')
        user_id = int(parts[2])
        plan_id = int(parts[3])
        
        # Get plan details
        plan = await db.get_plan_by_id(plan_id)
        if not plan:
            await query.answer("❌ Plan not found", show_alert=True)
            return
        
        # Create payment record
        payment_id = await db.create_payment(
            user_id=user_id,
            plan_id=plan_id,
            amount=plan['price'],
            file_id=None  # No file for subscription
        )
        
        # Approve payment
        success = await db.approve_payment(payment_id, query.from_user.id)
        
        if success:
            user = await db.get_user(user_id)
            lang = user.get('language_code', 'en')
            
            # Notify user
            text = BALANCE_TRANSLATIONS[lang]["payment_approved"]
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
            
            await query.edit_message_text(
                text=query.message.text + f"\n\n✅ <b>APPROVED</b> by @{query.from_user.username or query.from_user.first_name}\n"
                f"⏰ Approved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode=ParseMode.HTML
            )
            await query.answer("✅ Subscription approved!", show_alert=True)
    
    else:
        # Balance payment approval (existing logic)
        payment_id = int(query.data.split('_')[1])
        
        success = await db.approve_payment(payment_id, query.from_user.id)
        
        if success:
            payment = await db.get_payment(payment_id)
            user_id = payment['user_id']
            
            user = await db.get_user(user_id)
            lang = user.get('language_code', 'en')
            
            text = BALANCE_TRANSLATIONS[lang]["payment_approved"]
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
    
    # Check if it's subscription or balance payment
    if query.data.startswith('reject_sub_'):
        # Subscription rejection
        parts = query.data.split('_')
        user_id = int(parts[2])
        plan_id = int(parts[3])
        
        user = await db.get_user(user_id)
        lang = user.get('language_code', 'en')
        
        # Notify user
        text = BALANCE_TRANSLATIONS[lang]["payment_rejected"].format(ADMIN_USERNAME=ADMIN_USERNAME)
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        
        await query.edit_message_text(
            text=query.message.text + f"\n\n❌ <b>REJECTED</b> by @{query.from_user.username or query.from_user.first_name}\n"
            f"⏰ Rejected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode=ParseMode.HTML
        )
        await query.answer("❌ Subscription rejected", show_alert=True)
    
    else:
        # Balance payment rejection (existing logic)
        payment_id = int(query.data.split('_')[1])
        
        success = await db.reject_payment(payment_id, query.from_user.id, "Rejected by admin")
        
        if success:
            payment = await db.get_payment(payment_id)
            user_id = payment['user_id']
            
            user = await db.get_user(user_id)
            lang = user.get('language_code', 'en')
            
            text = BALANCE_TRANSLATIONS[lang]["payment_rejected"].format(ADMIN_USERNAME=ADMIN_USERNAME)
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

async def back_to_topup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to top-up menu"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['awaiting_custom_amount'] = False
    
    user = await db.get_user(query.from_user.id)
    lang = user.get('language_code', 'en') if user else 'en'
    
    text = BALANCE_TRANSLATIONS[lang]["topup_title"] + "\n\n"
    text += BALANCE_TRANSLATIONS[lang]["select_amount"]
    
    keyboard = [
        [
            InlineKeyboardButton("10,000 UZS", callback_data="topup_10k"),
            InlineKeyboardButton("25,000 UZS", callback_data="topup_25k"),
        ],
        [
            InlineKeyboardButton("50,000 UZS", callback_data="topup_50k"),
            InlineKeyboardButton("100,000 UZS", callback_data="topup_100k"),
        ],
        [
            InlineKeyboardButton(
                BALANCE_TRANSLATIONS[lang]["custom_amount"],
                callback_data="topup_custom"
            )
        ]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )