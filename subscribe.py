"""
Force Subscription Module for File Converter Bot
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ChatMemberStatus

logger = logging.getLogger(__name__)

# Configuration
FORCE_SUBSCRIPTION_ENABLED = True

REQUIRED_CHANNELS = [
        # {
        #     'id': '@Muslimbek_01',
        #     'name': 'Simple Slides | Rasmiy kanal',
        #     'url': 'https://t.me/muslimbek_01'
        # },

        # {
        #     'id': '@uzbek_europe',  
        #     'name': 'Simple Slides | Rasmiy kanal',
        #     'url': 'https://t.me/uzbek_europe'
        # },

        {
            'id': '@talabaga_tezkor_yordam',  
            'name': 'Talabalarga sifatli yordam',
            'url': 'https://t.me/talabaga_tezkor_yordam'
        },


        # {
        #     'id': '@Intellektualyoshlar',
        #     'name': 'Simple Slides | Rasmiy kanal',
        #     'url': 'https://t.me/intellektualyoshlar'
        # },
        # {
        #     'id': '@rus_tilidan_milliy_sertifikat',
        #     'name': 'Rus tilidan milliy sertifikat',
        #     'url': 'https://t.me/rus_tilidan_milliy_sertifikat'
        # },
        # {
        #     'id': '@Simple_slides',
        #     'name': 'Simple Slides | Rasmiy kanal',
        #     'url': 'https://t.me/simple_slides'
        # },
        # {
        #     'id': '@achieversC1r',
        #     'name': 'The Best English Channel',
        #     'url': 'https://t.me/achieversC1r'
        # },
        # {
        #     'id': '@Ai_zonez',
        #     'name': 'AI yangiliklari',
        #     'url': 'https://t.me/ai_zonez'
        # },
        # {
        #     'id': '@byabdumutalibovadilnoza',
        #     'name': 'Dilnoza Abdumutalibova | IELTS 8',
        #     'url': 'https://t.me/byabdumutalibovadilnoza'
        # },
        # {
        #     'id': '@simple_englishs',
        #     'name': 'Simple English',
        #     'url': 'https://t.me/simple_englishs'
        # },
        # {
        #     'id': '@grands_scholarships',
        #     'name': 'Grantlar va Scholarshiplar',
        #     'url': 'https://t.me/grands_scholarships'
        # },
]

# Subscription messages in multiple languages
SUBSCRIPTION_MESSAGES = {
    'uz': {
        'title': '🌟 <b>File Converter ga xush kelibsiz!</b>',
        'instruction': (
            'Botdan foydalanish uchun quyidagi kanallarga obuna bo\'ling 👇\n\n'
            '📌 <i>Bu bizga botni bepul va sifatli qilishga yordam beradi.</i>'
        ),
        'subscribe_btn': '📢 ',
        'check_btn': '✅ Obunani Tekshirish',
        'success': (
            '🎉 <b>Ajoyib!</b>\n\n'
            'Hammasi tayyor ✅ Endi botdan foydalanishingiz mumkin.\n\n'
            '👉 /start ni bosing va faylni yuboring!'
        ),
        'still_required': (
            '❌ <b>Deyarli tayyor!</b>\n\n'
            'Siz hali kanalga obuna bo\'lmadingiz.\n\n'
            '🔁 Iltimos, kanalga obuna bo\'lib, qayta tekshiring.'
        ),
        'checking': '🔍 <b>Obuna tekshirilmoqda...</b>\n\n⏳ Biroz kuting.',
        'error': '❌ <b>Xatolik yuz berdi</b>\n\nIltimos, /start ni qayta yuboring.'
    },
    'en': {
        'title': '🌟 <b>Welcome to File Converter!</b>',
        'instruction': (
            'To use this bot, please subscribe to our channel below 👇\n\n'
            '📌 <i>This helps us keep the bot free and improve it.</i>'
        ),
        'subscribe_btn': '📢 ',
        'check_btn': '✅ I Subscribed',
        'success': (
            '🎉 <b>Perfect!</b>\n\n'
            'You\'re all set ✅ You can now use the bot.\n\n'
            '👉 Type /start and send your file!'
        ),
        'still_required': (
            '❌ <b>Almost there!</b>\n\n'
            'You haven\'t subscribed to the channel yet.\n\n'
            '🔁 Please subscribe and try again.'
        ),
        'checking': '🔍 <b>Checking subscription...</b>\n\n⏳ Please wait.',
        'error': '❌ <b>Something went wrong</b>\n\nPlease send /start again.'
    },
    'ru': {
        'title': '🌟 <b>Добро пожаловать в File Converter!</b>',
        'instruction': (
            'Чтобы пользоваться ботом, подпишитесь на наш канал ниже 👇\n\n'
            '📌 <i>Это помогает нам поддерживать бот бесплатным.</i>'
        ),
        'subscribe_btn': '📢 ',
        'check_btn': '✅ Я подписался',
        'success': (
            '🎉 <b>Отлично!</b>\n\n'
            'Все готово ✅ Вы можете пользоваться ботом.\n\n'
            '👉 Напишите /start и отправьте файл!'
        ),
        'still_required': (
            '❌ <b>Почти готово!</b>\n\n'
            'Вы еще не подписались на канал.\n\n'
            '🔁 Пожалуйста, подпишитесь и попробуйте снова.'
        ),
        'checking': '🔍 <b>Проверяем подписку...</b>\n\n⏳ Подождите.',
        'error': '❌ <b>Что-то пошло не так</b>\n\nПожалуйста, отправьте /start снова.'
    }
}


async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> dict:
    """Check if user is subscribed to all required channels"""
    if not FORCE_SUBSCRIPTION_ENABLED:
        return {'is_subscribed': True, 'unsubscribed_channels': []}
    
    unsubscribed = []
    
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(
                chat_id=channel['id'],
                user_id=user_id
            )
            
            if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
                unsubscribed.append(channel)
                logger.info(f"User {user_id} NOT subscribed to {channel['name']}")
            else:
                logger.info(f"User {user_id} IS subscribed to {channel['name']}")
                
        except Exception as e:
            logger.error(f"Error checking subscription for {channel['id']}: {e}")
            unsubscribed.append(channel)
    
    return {
        'is_subscribed': len(unsubscribed) == 0,
        'unsubscribed_channels': unsubscribed
    }


def get_subscription_keyboard(unsubscribed_channels: list, language: str = 'en'):
    """Create subscription keyboard"""
    texts = SUBSCRIPTION_MESSAGES.get(language, SUBSCRIPTION_MESSAGES['en'])
    keyboard = []
    
    for channel in unsubscribed_channels:
        keyboard.append([
            InlineKeyboardButton(
                f"{texts['subscribe_btn']}{channel['name']}", 
                url=channel['url']
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            texts['check_btn'],
            callback_data='check_subscription'
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)


async def handle_subscription_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subscription check callback"""
    query = update.callback_query
    user = query.from_user
    
    # Get user from database to get language
    from database import DatabaseManager
    db = DatabaseManager()
    db_user = await db.get_user(user.id)
    lang = db_user.get('language_code', 'en') if db_user else 'en'
    
    texts = SUBSCRIPTION_MESSAGES.get(lang, SUBSCRIPTION_MESSAGES['en'])
    
    await query.answer(texts['checking'], show_alert=False)
    await query.edit_message_text(texts['checking'], parse_mode='HTML')
    
    try:
        status = await check_subscription(user.id, context)
        
        if status['is_subscribed']:
            await query.edit_message_text(texts['success'], parse_mode='HTML')
            logger.info(f"User {user.id} completed subscription requirements")
        else:
            keyboard = get_subscription_keyboard(status['unsubscribed_channels'], lang)
            await query.edit_message_text(
                texts['still_required'],
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            logger.info(f"User {user.id} still not subscribed")
            
    except Exception as e:
        logger.error(f"Error in subscription check: {e}")
        await query.edit_message_text(texts['error'], parse_mode='HTML')


async def require_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE, db_user: dict) -> bool:
    """
    Check subscription and show message if not subscribed
    Returns True if subscribed, False otherwise
    """
    if not FORCE_SUBSCRIPTION_ENABLED:
        return True
    
    user = update.effective_user
    lang = db_user.get('language_code', 'en')
    
    status = await check_subscription(user.id, context)
    
    if not status['is_subscribed']:
        texts = SUBSCRIPTION_MESSAGES.get(lang, SUBSCRIPTION_MESSAGES['en'])
        message = f"{texts['title']}\n\n{texts['instruction']}"
        keyboard = get_subscription_keyboard(status['unsubscribed_channels'], lang)
        
        await update.message.reply_text(
            message,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        logger.info(f"Blocked user {user.id} - not subscribed")
        return False
    
    return True


def setup_subscription_handlers(application):
    """Setup subscription callback handlers"""
    application.add_handler(CallbackQueryHandler(
        handle_subscription_check,
        pattern='^check_subscription$'
    ))
    logger.info("Subscription handlers registered")