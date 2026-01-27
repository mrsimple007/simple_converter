from telegram import InlineKeyboardButton, InlineKeyboardMarkup


TRANSLATIONS = {
    'en': {
        # General - Free tier
        'welcome_free': (
            "🌟 <b>Welcome to Simple File Converter!</b>\n\n"
            "I can convert files between various formats:\n"
            "📄 Documents (PDF, DOCX, TXT, PPTX, XLSX, etc.)\n"
            "🖼 Images (JPG, PNG, WEBP, SVG, etc.)\n"
            "🎵 Audio (MP3, WAV, AAC, OGG, FLAC)\n"
            "🎥 Video (MP4, MKV, AVI, MOV, GIF)\n"
            "🗜 Archives (ZIP, TAR, RAR)\n"
            "🧾 Data (JSON, CSV, XML, Markdown)\n\n"
            "Simply send me a file and I'll show you available conversion options!"
        ),
        
        # General - Premium tierUni
        'welcome_premium': (
            "🌟 <b>Welcome to Simple File Converter!</b>\n\n"
            "💎 <b>PREMIUM USER - Enjoy:</b>\n"
            "• ♾️ Unlimited conversions\n"
            "• 📦 Max file size: 500 MB\n"
            "• ⚡ Priority processing\n\n"
            "I can convert files between various formats:\n"
            "📄 Documents (PDF, DOCX, TXT, PPTX, XLSX, etc.)\n"
            "🖼 Images (JPG, PNG, WEBP, SVG, etc.)\n"
            "🎵 Audio (MP3, WAV, AAC, OGG, FLAC)\n"
            "🎥 Video (MP4, MKV, AVI, MOV, GIF)\n"
            "🗜 Archives (ZIP, TAR, RAR)\n"
            "🧾 Data (JSON, CSV, XML, Markdown)\n\n"
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
            "/subscribe - View premium plans\n"
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
            "ℹ️ <b>Simple File Converter </b>\n\n"
            "Version: 1.0.0\n"
            "Developer: @Muslimbek_01\n\n"
            "This bot helps you convert files between different formats quickly and easily.\n\n"
            "For support, contact: @SimpleLearn_main_admin"
        ),
        
        # Premium/Subscription
        'upgrade_to_premium': (
            "💎 <b>Upgrade to Premium</b>\n\n"
            "📊 <b>Your current usage:</b>\n"
            "Free Plan: {conversions_today}/{daily_limit} conversions today\n\n"
            "🚀 <b>Premium Benefits:</b>\n"
            "• ♾️ Unlimited conversions\n"
            "• 📦 500 MB file size (vs 25 MB)\n"
            "• ⚡ Priority processing\n"
            "• 🎯 No daily limits\n\n"
            "💰 <b>Premium Plans:</b>\n\n"
            "📅 <b>Monthly</b> - 10,000 UZS\n"
            "📅 <b>Quarterly (3 months)</b> - 25,000 UZS (Save 17%!)\n"
            "📅 <b>Yearly (12 months)</b> - 80,000 UZS (Save 33%!)\n\n"
            "💳 <b>Payment Card:</b> {card_number}\n\n"
            "Choose a plan below:"
        ),
        
        'premium_active': (
            "✅ <b>Your Premium Subscription is Active</b>\n\n"
            "💎 Enjoy unlimited conversions!\n"
            "Expires: {expiry_date}\n"
            "Conversions today: {conversions_today}\n\n"
            "Thank you for supporting us! 🎉"
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
        
        # File conversion
        'processing': "⏳ Processing your file...",
        'converting': "⏳ Converting to {format}...",
        'select_format': "📤 Select target format:",
        'select_format_with_limit': (
            "📤 <b>Select target format:</b>\n\n"
            "🆓 Remaining today: {remaining} conversions\n"
            "💡 Get unlimited with /subscribe"
        ),
        'conversion_success': "✅ Conversion complete! Here's your file:",
        'conversion_failed': "❌ Conversion failed: {error}",
        
        # Limits - Free tier
        'file_too_large_free': (
            "❌ <b>File too large for Free plan</b>\n\n"
            "Your file exceeds the 25 MB limit for free users.\n\n"
            "💎 <b>Upgrade to Premium</b> for:\n"
            "• 500 MB file size limit\n"
            "• Unlimited conversions\n\n"
            "Use /subscribe to upgrade!"
        ),
        
        'limit_reached_free': (
            "⚠️ <b>Daily limit reached!</b>\n\n"
            "You've used all 10 free conversions for today.\n\n"
            "💎 <b>Upgrade to Premium</b> for:\n"
            "• Unlimited conversions\n"
            "• 500 MB file size\n"
            "• No daily limits\n\n"
            "Or wait until tomorrow to get 10 more free conversions!"
        ),
        
        # Limits - Premium tier
        'file_too_large_premium': (
            "❌ <b>File too large</b>\n\n"
            "Maximum file size: {max_size} MB\n"
            "Your file exceeds this limit."
        ),
        
        'limit_reached_premium': (
            "⚠️ You've reached today's limit. Please try tomorrow."
        ),
        
        'unsupported_format': "❌ This format is not supported for conversion.",
        'invalid_file': "❌ Invalid file. Please send a valid file.",
        
        # Admin
        'new_payment': (
            "💰 <b>New Payment Received</b>\n\n"
            "User: {user}\n"
            "Plan: {plan}\n"
            "Amount: {amount} UZS\n"
            "User ID: {user_id}"
        ),
        'payment_approved': "✅ Your payment has been approved! Premium activated. 🎉",
        'payment_rejected': "❌ Your payment was rejected. Reason: {reason}\nPlease contact support.",
        
        # Buttons
        'btn_subscribe': "💎 Upgrade to Premium",
        'btn_upgrade': "💎 Upgrade Now",
        'btn_monthly': "📅 Monthly - 10,000 UZS",
        'btn_quarterly': "📅 3 Months - 25,000 UZS",
        'btn_yearly': "📅 12 Months - 80,000 UZS",
        'btn_approve': "✅ Approve",
        'btn_reject': "❌ Reject",
        'btn_cancel': "❌ Cancel",
        'select_category': "📁 What type of file do you want to convert?",
        'send_pdf': "📄 Please send your PDF file that you want to convert.",
        'send_word': "📝 Please send your Word document (DOC/DOCX).",
        'send_image': "🖼 Please send your image file (JPG, PNG, etc.).",
        'send_excel': "📊 Please send your Excel file (XLS/XLSX).",
        'send_audio': "🎵 Please send your audio file (MP3, WAV, etc.).",
        'send_video': "🎬 Please send your video file (MP4, AVI, etc.).",
        'send_ppt': "📑 Please send your PowerPoint file (PPT/PPTX).",
        'send_other': "📎 Please send your file.",
        'btn_back': "⬅️ Back",





    },
    
    'ru': {
        # General - Free tier
        'welcome_free': (
            "🌟 <b>Добро пожаловать в Simple File Converter!</b>\n\n"
            "Я могу конвертировать файлы между различными форматами:\n"
            "📄 Документы (PDF, DOCX, TXT, PPTX, XLSX и др.)\n"
            "🖼 Изображения (JPG, PNG, WEBP, SVG и др.)\n"
            "🎵 Аудио (MP3, WAV, AAC, OGG, FLAC)\n"
            "🎥 Видео (MP4, MKV, AVI, MOV, GIF)\n"
            "🗜 Архивы (ZIP, TAR, RAR)\n"
            "🧾 Данные (JSON, CSV, XML, Markdown)\n\n"
            "Просто отправьте мне файл!"
        ),
        
        # General - Premium tier
        'welcome_premium': (
            "🌟 <b>Добро пожаловать в Simple File Converter!</b>\n\n"
            "💎 <b>ПРЕМИУМ ПОЛЬЗОВАТЕЛЬ - Наслаждайтесь:</b>\n"
            "• ♾️ Безлимитные конвертации\n"
            "• 📦 Макс. размер: 500 МБ\n"
            "• ⚡ Приоритетная обработка\n\n"
            "Я могу конвертировать файлы между различными форматами:\n"
            "📄 Документы (PDF, DOCX, TXT, PPTX, XLSX и др.)\n"
            "🖼 Изображения (JPG, PNG, WEBP, SVG и др.)\n"
            "🎵 Аудио (MP3, WAV, AAC, OGG, FLAC)\n"
            "🎥 Видео (MP4, MKV, AVI, MOV, GIF)\n"
            "🗜 Архивы (ZIP, TAR, RAR)\n"
            "🧾 Данные (JSON, CSV, XML, Markdown)\n\n"
            "Просто отправьте мне файл!"
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
            "/formats - Список форматов\n"
            "/subscribe - Премиум планы\n"
            "/info - О боте\n"
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
            "ℹ️ <b>Simple File Converter Bot</b>\n\n"
            "Версия: 1.0.0\n"
            "Разработчик: @SimpleLearn_main_admin\n\n"
            "Этот бот помогает быстро конвертировать файлы.\n\n"
            "Поддержка: @SimpleLearn_main_admin"
        ),
        
        # Premium/Subscription
        'upgrade_to_premium': (
            "💎 <b>Обновление до Премиум</b>\n\n"
            "📊 <b>Ваше использование:</b>\n"
            "Бесплатный план: {conversions_today}/{daily_limit} конвертаций сегодня\n\n"
            "🚀 <b>Преимущества Премиум:</b>\n"
            "• ♾️ Безлимитные конвертации\n"
            "• 📦 500 МБ размер файла (vs 25 МБ)\n"
            "• ⚡ Приоритетная обработка\n"
            "• 🎯 Без дневных лимитов\n\n"
            "💰 <b>Планы:</b>\n\n"
            "📅 <b>Месяц</b> - 10,000 сум\n"
            "📅 <b>3 месяца</b> - 25,000 сум (Экономия 17%!)\n"
            "📅 <b>12 месяцев</b> - 80,000 сум (Экономия 33%!)\n\n"
            "💳 <b>Карта:</b> {card_number}\n\n"
            "Выберите план:"
        ),
        
        'premium_active': (
            "✅ <b>Ваша Премиум подписка активна</b>\n\n"
            "💎 Наслаждайтесь безлимитом!\n"
            "Истекает: {expiry_date}\n"
            "Конвертаций сегодня: {conversions_today}\n\n"
            "Спасибо за поддержку! 🎉"
        ),
        
        'payment_instructions': (
            "💳 <b>Инструкция по оплате:</b>\n\n"
            "1️⃣ Переведите <b>{amount} сум</b> на:\n"
            "   Карта: <code>{card_number}</code>\n\n"
            "2️⃣ Сделайте скриншот платежа\n\n"
            "3️⃣ Отправьте скриншот мне\n\n"
            "✅ Проверка в течение 24 часов."
        ),
        
        'payment_proof_sent': (
            "✅ <b>Подтверждение получено!</b>\n\n"
            "Платеж проверяется администратором.\n"
            "Вы получите уведомление после одобрения.\n\n"
            "⏳ Обычно до 24 часов."
        ),
        
        # File conversion
        'processing': "⏳ Обрабатываю файл...",
        'converting': "⏳ Конвертирую в {format}...",
        'select_format': "📤 Выберите формат:",
        'select_format_with_limit': (
            "📤 <b>Выберите формат:</b>\n\n"
            "🆓 Осталось сегодня: {remaining} конвертаций\n"
            "💡 Безлимит с /subscribe"
        ),
        'conversion_success': "✅ Готово! Вот ваш файл:",
        'conversion_failed': "❌ Ошибка: {error}",
        
        # Limits - Free tier
        'file_too_large_free': (
            "❌ <b>Файл слишком большой для бесплатного плана</b>\n\n"
            "Ваш файл превышает лимит 25 МБ.\n\n"
            "💎 <b>Обновитесь до Премиум</b>:\n"
            "• Лимит 500 МБ\n"
            "• Безлимитные конвертации\n\n"
            "Используйте /subscribe!"
        ),
        
        'limit_reached_free': (
            "⚠️ <b>Дневной лимит достигнут!</b>\n\n"
            "Вы использовали все 10 бесплатных конвертаций.\n\n"
            "💎 <b>Обновитесь до Премиум</b>:\n"
            "• Безлимитные конвертации\n"
            "• 500 МБ размер файла\n"
            "• Без дневных лимитов\n\n"
            "Или подождите до завтра!"
        ),
        
        # Limits - Premium tier
        'file_too_large_premium': (
            "❌ <b>Файл слишком большой</b>\n\n"
            "Максимум: {max_size} МБ"
        ),
        
        'limit_reached_premium': (
            "⚠️ Лимит достигнут. Попробуйте завтра."
        ),
        
        'unsupported_format': "❌ Формат не поддерживается.",
        'invalid_file': "❌ Неверный файл.",
        
        # Admin
        'new_payment': (
            "💰 <b>Новый платеж</b>\n\n"
            "Пользователь: {user}\n"
            "План: {plan}\n"
            "Сумма: {amount} сум\n"
            "ID: {user_id}"
        ),
        'payment_approved': "✅ Платеж одобрен! Премиум активирован. 🎉",
        'payment_rejected': "❌ Платеж отклонен. Причина: {reason}\nСвяжитесь с поддержкой.",
        
        # Buttons
        'btn_subscribe': "💎 Обновиться до Премиум",
        'btn_upgrade': "💎 Обновить сейчас",
        'btn_monthly': "📅 Месяц - 10,000 сум",
        'btn_quarterly': "📅 3 месяца - 25,000 сум",
        'btn_yearly': "📅 12 месяцев - 80,000 сум",
        'btn_approve': "✅ Одобрить",
        'btn_reject': "❌ Отклонить",
        'btn_cancel': "❌ Отмена",

        'select_category': "📁 Какой тип файла вы хотите конвертировать?",
        'send_pdf': "📄 Пожалуйста, отправьте PDF файл для конвертации.",
        'send_word': "📝 Пожалуйста, отправьте документ Word (DOC/DOCX).",
        'send_image': "🖼 Пожалуйста, отправьте изображение (JPG, PNG и т.д.).",
        'send_excel': "📊 Пожалуйста, отправьте Excel файл (XLS/XLSX).",
        'send_audio': "🎵 Пожалуйста, отправьте аудио файл (MP3, WAV и т.д.).",
        'send_video': "🎬 Пожалуйста, отправьте видео файл (MP4, AVI и т.д.).",
        'send_ppt': "📑 Пожалуйста, отправьте PowerPoint файл (PPT/PPTX).",
        'send_other': "📎 Пожалуйста, отправьте файл.",
        'btn_back': "⬅️ Назад",
















    },
    
    'uz': {
        # General - Free tier
        'welcome_free': (
            "🌟 <b>Simple File Converter ga xush kelibsiz!</b>\n\n"
            "Men fayllarni turli formatlar orasida o'zgartira olaman:\n"
            "📄 Hujjatlar (PDF, DOCX, TXT, PPTX, XLSX va boshqalar)\n"
            "🖼 Rasmlar (JPG, PNG, WEBP, SVG va boshqalar)\n"
            "🎵 Audio (MP3, WAV, AAC, OGG, FLAC)\n"
            "🎥 Video (MP4, MKV, AVI, MOV, GIF)\n"
            "🗜 Arxivlar (ZIP, TAR, RAR)\n"
            "🧾 Ma'lumotlar (JSON, CSV, XML, Markdown)\n\n"
            "Shunchaki menga faylni yuboring!"
        ),
        
        # General - Premium tier
        'welcome_premium': (
            "🌟 <b>Simple File Converter ga xush kelibsiz!</b>\n\n"
            "💎 <b>PREMIUM FOYDALANUVCHI - Mazza qilib ishlating:</b>\n"
            "• ♾️ Cheksiz konvertatsiyalar\n"
            "• 📦 Maks. hajm: 500 MB\n"
            "• ⚡ Tezkor ishlov\n\n"
            "Men fayllarni turli formatlar orasida o'zgartira olaman:\n"
            "📄 Hujjatlar (PDF, DOCX, TXT, PPTX, XLSX va boshqalar)\n"
            "🖼 Rasmlar (JPG, PNG, WEBP, SVG va boshqalar)\n"
            "🎵 Audio (MP3, WAV, AAC, OGG, FLAC)\n"
            "🎥 Video (MP4, MKV, AVI, MOV, GIF)\n"
            "🗜 Arxivlar (ZIP, TAR, RAR)\n"
            "🧾 Ma'lumotlar (JSON, CSV, XML, Markdown)\n\n"
            "Shunchaki menga faylni yuboring!"
        ),
        
        'language_selected': "✅ Til o'zbekcha qilib o'rnatildi! /start bilan botni boshlashingiz mumkin.",
        'select_language': "🌍 Iltimos, tilni tanlang:",
        
        'help': (
            "📖 <b>Qanday foydalanish:</b>\n\n"
            "1️⃣ Menga istalgan faylni yuboring\n"
            "2️⃣ Kerakli formatni tanlang\n"
            "3️⃣ Konvertatsiyani kuting\n"
            "4️⃣ Faylingizni yuklab oling!\n\n"
            "🔹 Buyruqlar:\n"
            "/start - Botni boshlash\n"
            "/help - Yordam\n"
            "/formats - Formatlar ro'yxati\n"
            "/subscribe - Premium rejalar\n"
            "/info - Bot haqida\n"
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
            "ℹ️ <b>Simple File Converter Bot</b>\n\n"
            "Versiya: 1.0.0\n"
            "Dasturchi: @Muslimbek_01\n\n"
            "Bu bot fayllarni tez konvertatsiya qilishda yordam beradi.\n\n"
            "Qo'llab-quvvatlash: @SimpleLearn_main_admin"
        ),
        
        # Premium/Subscription
        'upgrade_to_premium': (
            "💎 <b>Premium'ga o'tish</b>\n\n"
            "📊 <b>Sizning foydalanishingiz:</b>\n"
            "Bepul reja: {conversions_today}/{daily_limit} konvertatsiya bugun\n\n"
            "🚀 <b>Premium imtiyozlari:</b>\n"
            "• ♾️ Cheksiz konvertatsiyalar\n"
            "• 📦 500 MB fayl hajmi (vs 25 MB)\n"
            "• ⚡ Tezkor ishlov\n"
            "• 🎯 Kunlik cheklovlar yo'q\n\n"
            "💰 <b>Rejalar:</b>\n\n"
            "📅 <b>Oylik</b> - 10,000 so'm\n"
            "📅 <b>3 oy</b> - 25,000 so'm (17% tejash!)\n"
            "📅 <b>12 oy</b> - 80,000 so'm (33% tejash!)\n\n"
            "💳 <b>To'lov kartasi:</b> {card_number}\n\n"
            "Rejani tanlang:"
        ),
        
        'premium_active': (
            "✅ <b>Premium obunangiz faol</b>\n\n"
            "💎 Cheksiz konvertatsiyadan bahramand bo'ling!\n"
            "Tugaydi: {expiry_date}\n"
            "Bugungi konvertatsiyalar: {conversions_today}\n\n"
            "Qo'llab-quvvatlaganingiz uchun rahmat! 🎉"
        ),
        
        'payment_instructions': (
            "💳 <b>To'lov ko'rsatmalari:</b>\n\n"
            "1️⃣ <b>{amount} so'm</b> ni quyidagi kartaga o'tkazing:\n"
            "   Karta: <code>{card_number}</code>\n\n"
            "2️⃣ To'lovning skrinshotini oling\n\n"
            "3️⃣ Skrinshotni menga yuboring\n\n"
            "✅ 24 soat ichida tekshiriladi."
        ),
        
        'payment_proof_sent': (
            "✅ <b>To'lov tasdigi qabul qilindi!</b>\n\n"
            "To'lovingiz admin tomonidan tekshirilmoqda.\n"
            "Tasdiqlangandan so'ng xabardor qilinasiz.\n\n"
            "⏳ Odatda 24 soatgacha."
        ),
        
        # File conversion
        'processing': "⏳ Fayl ishlanmoqda... Iltimos kuting...",
        'converting': "⏳ {format} formatiga o'zgartirilmoqda...",
        'select_format': "📤 Formatni tanlang:",
        'select_format_with_info': "📤 Formatni tanlang ({info}):",

# Limits - Free tier
    'file_too_large_free': (
        "❌ <b>Bepul reja uchun fayl juda katta</b>\n\n"
        "Sizning faylingiz 25 MB limitidan oshib ketdi.\n\n"
        "💎 <b>Premium'ga o'ting</b>:\n"
        "• 500 MB limit\n"
        "• Cheksiz konvertatsiyalar\n\n"
        "/subscribe dan foydalaning!"
    ),
    
    'limit_reached_free': (
        "⚠️ <b>Kunlik limit tugadi!</b>\n\n"
        "Siz barcha 30 ta bepul kunlik konvertatsiyani ishlatdingiz.\n\n"
        "💎 <b>Premium'ga o'ting</b>:\n"
        "• Cheksiz konvertatsiyalar\n"
        "• 500 MB fayl hajmi\n"
        "• Kunlik limitlar yo'q\n\n"
        "Yoki ertaga qayta urinib ko'ring!"
    ),
    
    # Limits - Premium tier
    'file_too_large_premium': (
        "❌ <b>Fayl hajmi juda katta</b>\n\n"
        "Maksimum: {max_size} MB"
    ),
    
    'limit_reached_premium': (
        "⚠️ Limit tugadi. Ertaga qayta urinib ko'ring."
    ),
    
    'unsupported_format': "❌ Format qo'llab-quvvatlanmaydi.",
    'invalid_file': "❌ Noto'g'ri fayl.",
    
    # Admin
    'new_payment': (
        "💰 <b>Yangi to'lov</b>\n\n"
        "Foydalanuvchi: {user}\n"
        "Reja: {plan}\n"
        "Summa: {amount} so'm\n"
        "ID: {user_id}"
    ),
    'payment_approved': "✅ To'lov tasdiqlandi! Premium faollashtirildi. 🎉",
    'payment_rejected': "❌ To'lov rad etildi. Sabab: {reason}\nQo'llab-quvvatlash bilan bog'laning.",
    
    # Buttons
    'btn_subscribe': "💎 Premium'ga o'tish",
    'btn_upgrade': "💎 Hozir yangilash",
    'btn_monthly': "📅 Oylik - 10,000 so'm",
    'btn_quarterly': "📅 3 oy - 25,000 so'm",
    'btn_yearly': "📅 12 oy - 80,000 so'm",
    'btn_approve': "✅ Tasdiqlash",
    'btn_reject': "❌ Rad etish",
    'btn_cancel': "❌ Bekor qilish",

    'select_format': "📤 O'zgartirmoqchi bo'lgan formatini tanlang:",
    'select_format_with_limit': "✅Faylingiz qabul qilindi! \n\n📤 O'zgartirmoqchi bo'lgan formatini tanlang:\n🆓 Bugun qolgan: {remaining} konvertatsiya\n💡 Cheksiz olish uchun /subscribe",
    'converting': "⏳ Fayl {format} formatiga konvertatsiya qilinmoqda...",
    'conversion_success': "✅ Konvertatsiya muvaffaqiyatli bajarildi! Mana sizning faylingiz:",
    'conversion_failed': "❌ Konvertatsiyada xato: {error}\n\nIltimos, qaytadan urinib ko'ring yoki boshqa formatni tanlang.",

    'select_category': (
        "📁 <b>Qaysi turdagi faylni konvertatsiya qilmoqchisiz?</b>\n\n"
        "Quyidagi variantlardan birini tanlang yoki mos bo‘lgan fayl turini belgilang 👇\n"
        "Bot sizga eng qulay formatni taklif qiladi."
    ),

    'send_pdf': (
        "📄 <b>PDF fayl yuboring</b>\n\n"
        "Iltimos, konvertatsiya qilmoqchi bo‘lgan PDF hujjatingizni yuboring.\n"
        "Masalan: PDF → Word, PDF → JPG va boshqalar."
    ),

    'send_word': (
        "📝 <b>Word hujjatini yuboring</b>\n\n"
        "Iltimos, DOC yoki DOCX formatdagi Word faylingizni yuboring.\n"
        "Masalan: Word → PDF yoki Word → TXT."
    ),

    'send_image': (
        "🖼 <b>Rasm yuboring</b>\n\n"
        "JPG, PNG yoki boshqa formatdagi rasm faylingizni yuboring.\n"
        "Masalan: JPG → PNG, rasm → PDF."
    ),

    'send_excel': (
        "📊 <b>Excel fayl yuboring</b>\n\n"
        "Iltimos, XLS yoki XLSX formatdagi Excel hujjatingizni yuboring.\n"
        "Masalan: Excel → PDF yoki Excel → CSV."
    ),

    'send_audio': (
        "🎵 <b>Audio fayl yuboring</b>\n\n"
        "MP3, WAV yoki boshqa audio faylingizni yuboring.\n"
        "Masalan: WAV → MP3 yoki audio → boshqa format."
    ),

    'send_video': (
        "🎬 <b>Video fayl yuboring</b>\n\n"
        "MP4, AVI yoki boshqa video faylingizni yuboring.\n"
        "Masalan: MP4 → AVI yoki video → audio."
    ),

    'send_ppt': (
        "📑 <b>PowerPoint fayl yuboring</b>\n\n"
        "PPT yoki PPTX formatdagi prezentatsiya faylingizni yuboring.\n"
        "Masalan: PPT → PDF yoki PPT → rasmlar."
    ),

    'send_other': (
        "📎 <b>Fayl yuboring</b>\n\n"
        "Agar faylingiz yuqoridagi toifalarga mos kelmasa, uni shu yerga yuboring.\n"
        "Bot formatni avtomatik aniqlashga harakat qiladi."
    ),
        'btn_back': "⬅️ Orqaga",























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