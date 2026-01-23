from telegram import InlineKeyboardButton, InlineKeyboardMarkup


TRANSLATIONS = {
    'en': {
        # General
        'welcome': (
            "🌟 <b>Welcome to Universal File Converter Bot!</b>\n\n"
            "I can convert files between various formats:\n"
            "📄 Documents (PDF, DOCX, TXT, PPTX, XLSX, etc.)\n"
            "🖼 Images (JPG, PNG, WEBP, SVG, etc.)\n"
            "🎵 Audio (MP3, WAV, AAC, OGG, FLAC)\n"
            "🎥 Video (MP4, MKV, AVI, MOV, GIF)\n"
            "🗜 Archives (ZIP, TAR, RAR)\n"
            "🧾 Data (JSON, CSV, XML, Markdown)\n\n"
            "📌 <b>To use the bot, you need an active subscription.</b>\n\n"
            "Simply send me a file and I'll show you available conversion options!"
        ),
        'language_selected': "✅ Language set to English",
        'select_language': "🌍 Please select your language:",
        'help': (
            "📖 <b>How to use:</b>\n\n"
            "1️⃣ Send me any file\n"
            "2️⃣ Choose the format you want\n"
            "3️⃣ Wait for conversion\n"
            "4️⃣ Download your file!\n\n"
            "🔹 Commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help\n"
            "/formats - List supported formats\n"
            "/subscribe - Manage subscription\n"
            "/info - Bot information\n"
            "/language - Change language"
        ),
        'formats': (
            "📋 <b>Supported Formats:</b>\n\n"
            "📄 <b>Documents:</b>\n"
            "PDF, DOCX, TXT, HTML, PPTX, XLSX, CSV, EPUB\n\n"
            "🖼 <b>Images:</b>\n"
            "JPG, PNG, WEBP, BMP, SVG\n\n"
            "🎵 <b>Audio:</b>\n"
            "MP3, WAV, AAC, OGG, FLAC\n\n"
            "🎥 <b>Video:</b>\n"
            "MP4, MKV, AVI, MOV, GIF\n\n"
            "🗜 <b>Archives:</b>\n"
            "ZIP, TAR, RAR\n\n"
            "🧾 <b>Data:</b>\n"
            "TXT, JSON, CSV, XML, MD, HTML"
        ),
        'info': (
            "ℹ️ <b>Universal File Converter Bot</b>\n\n"
            "Version: 1.0.0\n"
            "Developer: @SimpleLearn_main_admin\n\n"
            "This bot helps you convert files between different formats quickly and easily.\n\n"
            "For support, contact: @SimpleLearn_main_admin"
        ),
        
        # Subscription
        'subscription_required': (
            "⚠️ <b>Subscription Required</b>\n\n"
            "To use this bot, you need an active subscription.\n"
            "Use /subscribe to view available plans."
        ),
        'subscription_info': (
            "💎 <b>Subscription Plans:</b>\n\n"
            "📅 <b>Monthly</b> - 10,000 UZS\n"
            "• 50 conversions per day\n"
            "• Max file size: 100 MB\n\n"
            "📅 <b>Quarterly (3 months)</b> - 25,000 UZS\n"
            "• 100 conversions per day\n"
            "• Max file size: 200 MB\n\n"
            "📅 <b>Yearly (12 months)</b> - 80,000 UZS\n"
            "• Unlimited conversions\n"
            "• Max file size: 500 MB\n\n"
            "💳 <b>Payment Card:</b> {card_number}\n\n"
            "Choose a plan below:"
        ),
        'payment_instructions': (
            "💳 <b>Payment Instructions:</b>\n\n"
            "1️⃣ Transfer <b>{amount} UZS</b> to:\n"
            "   Card: <code>{card_number}</code>\n\n"
            "2️⃣ Take a screenshot of the payment\n\n"
            "3️⃣ Send the screenshot to me\n\n"
            "✅ Your payment will be verified within 24 hours."
        ),
        'payment_proof_sent': (
            "✅ <b>Payment proof received!</b>\n\n"
            "Your payment is being reviewed by an admin.\n"
            "You will be notified once it's approved.\n\n"
            "⏳ Usually takes up to 24 hours."
        ),
        'subscription_active': (
            "✅ <b>Your Subscription is Active</b>\n\n"
            "Expires: {expiry_date}\n"
            "Conversions today: {conversions_today}\n\n"
            "Thank you for using our service! 🎉"
        ),
        'subscription_expired': (
            "⚠️ <b>Your subscription has expired</b>\n\n"
            "Please renew to continue using the bot.\n"
            "Use /subscribe to view plans."
        ),
        
        # File conversion
        'processing': "⏳ Processing your file...",
        'converting': "⏳ Converting to {format}...",
        'select_format': "📤 Select target format:",
        'conversion_success': "✅ Conversion complete! Here's your file:",
        'conversion_failed': "❌ Conversion failed: {error}",
        'file_too_large': "❌ File is too large. Maximum size: {max_size} MB",
        'unsupported_format': "❌ This format is not supported for conversion.",
        'invalid_file': "❌ Invalid file. Please send a valid file.",
        'limit_reached': "⚠️ Daily conversion limit reached. Please try tomorrow or upgrade your plan.",
        
        # Admin
        'new_payment': (
            "💰 <b>New Payment Received</b>\n\n"
            "User: {user}\n"
            "Plan: {plan}\n"
            "Amount: {amount} UZS\n"
            "User ID: {user_id}"
        ),
        'payment_approved': "✅ Your payment has been approved! Subscription is now active. 🎉",
        'payment_rejected': "❌ Your payment was rejected. Reason: {reason}\nPlease contact support.",
        
        # Buttons
        'btn_subscribe': "💎 Subscribe",
        'btn_monthly': "📅 Monthly - 10,000 UZS",
        'btn_quarterly': "📅 3 Months - 25,000 UZS",
        'btn_yearly': "📅 12 Months - 80,000 UZS",
        'btn_approve': "✅ Approve",
        'btn_reject': "❌ Reject",
        'btn_cancel': "❌ Cancel",
    },
    
    'ru': {
        # General
        'welcome': (
            "🌟 <b>Добро пожаловать в Universal File Converter!</b>\n\n"
            "Я могу конвертировать файлы между различными форматами:\n"
            "📄 Документы (PDF, DOCX, TXT, PPTX, XLSX и др.)\n"
            "🖼 Изображения (JPG, PNG, WEBP, SVG и др.)\n"
            "🎵 Аудио (MP3, WAV, AAC, OGG, FLAC)\n"
            "🎥 Видео (MP4, MKV, AVI, MOV, GIF)\n"
            "🗜 Архивы (ZIP, TAR, RAR)\n"
            "🧾 Данные (JSON, CSV, XML, Markdown)\n\n"
            "📌 <b>Для использования бота необходима активная подписка.</b>\n\n"
            "Просто отправьте мне файл, и я покажу доступные варианты конвертации!"
        ),
        'language_selected': "✅ Язык установлен: Русский",
        'select_language': "🌍 Пожалуйста, выберите язык:",
        'help': (
            "📖 <b>Как использовать:</b>\n\n"
            "1️⃣ Отправьте мне любой файл\n"
            "2️⃣ Выберите нужный формат\n"
            "3️⃣ Дождитесь конвертации\n"
            "4️⃣ Скачайте ваш файл!\n\n"
            "🔹 Команды:\n"
            "/start - Запустить бота\n"
            "/help - Показать эту справку\n"
            "/formats - Список поддерживаемых форматов\n"
            "/subscribe - Управление подпиской\n"
            "/info - Информация о боте\n"
            "/language - Изменить язык"
        ),
        'formats': (
            "📋 <b>Поддерживаемые форматы:</b>\n\n"
            "📄 <b>Документы:</b>\n"
            "PDF, DOCX, TXT, HTML, PPTX, XLSX, CSV, EPUB\n\n"
            "🖼 <b>Изображения:</b>\n"
            "JPG, PNG, WEBP, BMP, SVG\n\n"
            "🎵 <b>Аудио:</b>\n"
            "MP3, WAV, AAC, OGG, FLAC\n\n"
            "🎥 <b>Видео:</b>\n"
            "MP4, MKV, AVI, MOV, GIF\n\n"
            "🗜 <b>Архивы:</b>\n"
            "ZIP, TAR, RAR\n\n"
            "🧾 <b>Данные:</b>\n"
            "TXT, JSON, CSV, XML, MD, HTML"
        ),
        'info': (
            "ℹ️ <b>Universal File Converter Bot</b>\n\n"
            "Версия: 1.0.0\n"
            "Разработчик: @SimpleLearn_main_admin\n\n"
            "Этот бот помогает быстро и легко конвертировать файлы между различными форматами.\n\n"
            "Поддержка: @SimpleLearn_main_admin"
        ),
        
        # Subscription
        'subscription_required': (
            "⚠️ <b>Требуется подписка</b>\n\n"
            "Для использования бота необходима активная подписка.\n"
            "Используйте /subscribe для просмотра доступных планов."
        ),
        'subscription_info': (
            "💎 <b>Тарифные планы:</b>\n\n"
            "📅 <b>Месячный</b> - 10,000 сум\n"
            "• 50 конвертаций в день\n"
            "• Макс. размер файла: 100 МБ\n\n"
            "📅 <b>Квартальный (3 месяца)</b> - 25,000 сум\n"
            "• 100 конвертаций в день\n"
            "• Макс. размер файла: 200 МБ\n\n"
            "📅 <b>Годовой (12 месяцев)</b> - 80,000 сум\n"
            "• Безлимитные конвертации\n"
            "• Макс. размер файла: 500 МБ\n\n"
            "💳 <b>Карта для оплаты:</b> {card_number}\n\n"
            "Выберите план ниже:"
        ),
        'payment_instructions': (
            "💳 <b>Инструкция по оплате:</b>\n\n"
            "1️⃣ Переведите <b>{amount} сум</b> на:\n"
            "   Карта: <code>{card_number}</code>\n\n"
            "2️⃣ Сделайте скриншот платежа\n\n"
            "3️⃣ Отправьте скриншот мне\n\n"
            "✅ Ваш платеж будет проверен в течение 24 часов."
        ),
        'payment_proof_sent': (
            "✅ <b>Подтверждение оплаты получено!</b>\n\n"
            "Ваш платеж проверяется администратором.\n"
            "Вы получите уведомление после одобрения.\n\n"
            "⏳ Обычно занимает до 24 часов."
        ),
        'subscription_active': (
            "✅ <b>Ваша подписка активна</b>\n\n"
            "Истекает: {expiry_date}\n"
            "Конвертаций сегодня: {conversions_today}\n\n"
            "Спасибо за использование нашего сервиса! 🎉"
        ),
        'subscription_expired': (
            "⚠️ <b>Ваша подписка истекла</b>\n\n"
            "Пожалуйста, продлите подписку для продолжения использования бота.\n"
            "Используйте /subscribe для просмотра планов."
        ),
        
        # File conversion
        'processing': "⏳ Обрабатываю ваш файл...",
        'converting': "⏳ Конвертирую в {format}...",
        'select_format': "📤 Выберите формат:",
        'conversion_success': "✅ Конвертация завершена! Вот ваш файл:",
        'conversion_failed': "❌ Ошибка конвертации: {error}",
        'file_too_large': "❌ Файл слишком большой. Максимальный размер: {max_size} МБ",
        'unsupported_format': "❌ Этот формат не поддерживается для конвертации.",
        'invalid_file': "❌ Неверный файл. Пожалуйста, отправьте корректный файл.",
        'limit_reached': "⚠️ Достигнут дневной лимит конвертаций. Попробуйте завтра или обновите тариф.",
        
        # Admin
        'new_payment': (
            "💰 <b>Новый платеж получен</b>\n\n"
            "Пользователь: {user}\n"
            "План: {plan}\n"
            "Сумма: {amount} сум\n"
            "ID пользователя: {user_id}"
        ),
        'payment_approved': "✅ Ваш платеж одобрен! Подписка активирована. 🎉",
        'payment_rejected': "❌ Ваш платеж отклонен. Причина: {reason}\nПожалуйста, свяжитесь с поддержкой.",
        
        # Buttons
        'btn_subscribe': "💎 Подписаться",
        'btn_monthly': "📅 Месяц - 10,000 сум",
        'btn_quarterly': "📅 3 месяца - 25,000 сум",
        'btn_yearly': "📅 12 месяцев - 80,000 сум",
        'btn_approve': "✅ Одобрить",
        'btn_reject': "❌ Отклонить",
        'btn_cancel': "❌ Отмена",
    },
    
    'uz': {
        # General
        'welcome': (
            "🌟 <b>Universal File Converter botiga xush kelibsiz!</b>\n\n"
            "Men fayllarni turli formatlar orasida o'zgartira olaman:\n"
            "📄 Hujjatlar (PDF, DOCX, TXT, PPTX, XLSX va boshqalar)\n"
            "🖼 Rasmlar (JPG, PNG, WEBP, SVG va boshqalar)\n"
            "🎵 Audio (MP3, WAV, AAC, OGG, FLAC)\n"
            "🎥 Video (MP4, MKV, AVI, MOV, GIF)\n"
            "🗜 Arxivlar (ZIP, TAR, RAR)\n"
            "🧾 Ma'lumotlar (JSON, CSV, XML, Markdown)\n\n"
            "📌 <b>Botdan foydalanish uchun faol obuna kerak.</b>\n\n"
            "Shunchaki menga fayl yuboring va men mavjud konvertatsiya variantlarini ko'rsataman!"
        ),
        'language_selected': "✅ Til o'zbekcha qilib o'rnatildi",
        'select_language': "🌍 Iltimos, tilni tanlang:",
        'help': (
            "📖 <b>Qanday foydalanish:</b>\n\n"
            "1️⃣ Menga istalgan faylni yuboring\n"
            "2️⃣ Kerakli formatni tanlang\n"
            "3️⃣ Konvertatsiyani kuting\n"
            "4️⃣ Faylingizni yuklab oling!\n\n"
            "🔹 Buyruqlar:\n"
            "/start - Botni ishga tushirish\n"
            "/help - Ushbu yordamni ko'rsatish\n"
            "/formats - Qo'llab-quvvatlanadigan formatlar ro'yxati\n"
            "/subscribe - Obunani boshqarish\n"
            "/info - Bot haqida ma'lumot\n"
            "/language - Tilni o'zgartirish"
        ),
        'formats': (
            "📋 <b>Qo'llab-quvvatlanadigan formatlar:</b>\n\n"
            "📄 <b>Hujjatlar:</b>\n"
            "PDF, DOCX, TXT, HTML, PPTX, XLSX, CSV, EPUB\n\n"
            "🖼 <b>Rasmlar:</b>\n"
            "JPG, PNG, WEBP, BMP, SVG\n\n"
            "🎵 <b>Audio:</b>\n"
            "MP3, WAV, AAC, OGG, FLAC\n\n"
            "🎥 <b>Video:</b>\n"
            "MP4, MKV, AVI, MOV, GIF\n\n"
            "🗜 <b>Arxivlar:</b>\n"
            "ZIP, TAR, RAR\n\n"
            "🧾 <b>Ma'lumotlar:</b>\n"
            "TXT, JSON, CSV, XML, MD, HTML"
        ),
        'info': (
            "ℹ️ <b>Universal File Converter Bot</b>\n\n"
            "Versiya: 1.0.0\n"
            "Dasturchi: @SimpleLearn_main_admin\n\n"
            "Ushbu bot fayllarni turli formatlar orasida tez va oson konvertatsiya qilishda yordam beradi.\n\n"
            "Qo'llab-quvvatlash: @SimpleLearn_main_admin"
        ),
        
        # Subscription
        'subscription_required': (
            "⚠️ <b>Obuna talab qilinadi</b>\n\n"
            "Botdan foydalanish uchun faol obuna kerak.\n"
            "Mavjud rejalarni ko'rish uchun /subscribe dan foydalaning."
        ),
        'subscription_info': (
            "💎 <b>Obuna rejalari:</b>\n\n"
            "📅 <b>Oylik</b> - 10,000 so'm\n"
            "• Kuniga 50 ta konvertatsiya\n"
            "• Maks. fayl hajmi: 100 MB\n\n"
            "📅 <b>Choraklik (3 oy)</b> - 25,000 so'm\n"
            "• Kuniga 100 ta konvertatsiya\n"
            "• Maks. fayl hajmi: 200 MB\n\n"
            "📅 <b>Yillik (12 oy)</b> - 80,000 so'm\n"
            "• Cheksiz konvertatsiyalar\n"
            "• Maks. fayl hajmi: 500 MB\n\n"
            "💳 <b>To'lov kartasi:</b> {card_number}\n\n"
            "Quyidan rejani tanlang:"
        ),
        'payment_instructions': (
            "💳 <b>To'lov ko'rsatmalari:</b>\n\n"
            "1️⃣ <b>{amount} so'm</b> ni quyidagi kartaga o'tkazing:\n"
            "   Karta: <code>{card_number}</code>\n\n"
            "2️⃣ To'lovning skrinshotini oling\n\n"
            "3️⃣ Skrinshotni menga yuboring\n\n"
            "✅ To'lovingiz 24 soat ichida tekshiriladi."
        ),
        'payment_proof_sent': (
            "✅ <b>To'lov tasdigi qabul qilindi!</b>\n\n"
            "To'lovingiz admin tomonidan tekshirilmoqda.\n"
            "Tasdiqlangandan so'ng xabardor qilinasiz.\n\n"
            "⏳ Odatda 24 soatgacha vaqt ketadi."
        ),
        'subscription_active': (
            "✅ <b>Obunangiz faol</b>\n\n"
            "Tugaydi: {expiry_date}\n"
            "Bugungi konvertatsiyalar: {conversions_today}\n\n"
            "Xizmatimizdan foydalanganingiz uchun rahmat! 🎉"
        ),
        'subscription_expired': (
            "⚠️ <b>Obunangiz tugadi</b>\n\n"
            "Botdan foydalanishni davom ettirish uchun obunani yangilang.\n"
            "Rejalarni ko'rish uchun /subscribe dan foydalaning."
        ),
        
        # File conversion
        'processing': "⏳ Faylingiz qayta ishlanmoqda...",
        'converting': "⏳ {format} formatiga o'zgartirilmoqda...",
        'select_format': "📤 Maqsad formatini tanlang:",
        'conversion_success': "✅ Konvertatsiya tugadi! Mana faylingiz:",
        'conversion_failed': "❌ Konvertatsiya xatosi: {error}",
        'file_too_large': "❌ Fayl juda katta. Maksimal hajm: {max_size} MB",
        'unsupported_format': "❌ Bu format konvertatsiya uchun qo'llab-quvvatlanmaydi.",
        'invalid_file': "❌ Noto'g'ri fayl. Iltimos, to'g'ri fayl yuboring.",
        'limit_reached': "⚠️ Kunlik konvertatsiya limiti tugadi. Ertaga qayta urinib ko'ring yoki rejani yangilang.",
        
        # Admin
        'new_payment': (
            "💰 <b>Yangi to'lov qabul qilindi</b>\n\n"
            "Foydalanuvchi: {user}\n"
            "Reja: {plan}\n"
            "Summa: {amount} so'm\n"
            "Foydalanuvchi ID: {user_id}"
        ),
        'payment_approved': "✅ To'lovingiz tasdiqlandi! Obuna faollashtirildi. 🎉",
        'payment_rejected': "❌ To'lovingiz rad etildi. Sabab: {reason}\nIltimos, qo'llab-quvvatlash bilan bog'laning.",
        
        # Buttons
        'btn_subscribe': "💎 Obuna bo'lish",
        'btn_monthly': "📅 Oylik - 10,000 so'm",
        'btn_quarterly': "📅 3 oy - 25,000 so'm",
        'btn_yearly': "📅 12 oy - 80,000 so'm",
        'btn_approve': "✅ Tasdiqlash",
        'btn_reject': "❌ Rad etish",
        'btn_cancel': "❌ Bekor qilish",
    }
}


def get_text(lang: str, key: str, **kwargs) -> str:
    """Get translated text for a given language and key"""
    if lang not in TRANSLATIONS:
        lang = 'en'
    
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, key))
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    
    return text


def get_language_keyboard():
    """Get language selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        ],
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)