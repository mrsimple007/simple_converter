# Universal File Converter Telegram Bot

A powerful Telegram bot that converts files between various formats with subscription management and multi-language support (English, Russian, Uzbek).

## Features

- 📄 **Document Conversion**: PDF, DOCX, TXT, PPTX, XLSX, CSV
- 🖼 **Image Conversion**: JPG, PNG, WEBP, BMP, SVG
- 🎵 **Audio Conversion**: MP3, WAV, AAC, OGG, FLAC
- 🎥 **Video Conversion**: MP4, MKV, AVI, MOV, GIF
- 🗜 **Archive Support**: ZIP, TAR
- 🧾 **Data Formats**: JSON, CSV, XML, Markdown
- 💎 **Subscription Management**: Multiple subscription tiers
- 🌍 **Multi-language**: English, Russian, Uzbek
- 👨‍💼 **Admin Panel**: Payment approval system

## Prerequisites

### System Requirements
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    ffmpeg \
    imagemagick \
    libreoffice \
    pandoc \
    python3-pip

# For production, also install:
sudo apt-get install -y \
    ghostscript \
    poppler-utils
```

### Python Requirements
- Python 3.8 or higher
- pip

## Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd telegram-converter-bot
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Supabase Database

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL script from `db_schema.sql` in the Supabase SQL editor
3. Get your project URL and anon key from Settings → API

### 4. Configure Environment Variables

Create a `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
BOT_TOKEN=your_telegram_bot_token
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
ADMIN_CHAT_ID=your_telegram_user_id
```

### 5. Create Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token to your `.env` file

## Project Structure

```
├── bot.py              # Main bot implementation
├── database.py         # Database manager (Supabase)
├── converters.py       # File conversion logic
├── translations.py     # Multi-language support
├── db_schema.sql       # Database schema
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## Usage

### Starting the Bot

```bash
python bot.py
```

### User Commands

- `/start` - Start the bot and select language
- `/help` - Show help message
- `/formats` - List supported formats
- `/subscribe` - View and purchase subscriptions
- `/info` - Bot information
- `/language` - Change language

### Converting Files

1. Send any supported file to the bot
2. Select target format from the buttons
3. Wait for conversion
4. Download your converted file

### Subscription Plans

The bot includes three subscription tiers:

1. **Monthly** (10,000 UZS)
   - 50 conversions per day
   - Max file size: 100 MB

2. **Quarterly** (25,000 UZS)
   - 100 conversions per day
   - Max file size: 200 MB

3. **Yearly** (80,000 UZS)
   - Unlimited conversions
   - Max file size: 500 MB

### Payment Process

1. User selects a subscription plan
2. Bot shows payment instructions with card number
3. User transfers money and sends payment screenshot
4. Admin receives notification with approve/reject buttons
5. Upon approval, user's subscription is activated

## Admin Features

Admins (configured in `NOTIFICATION_ADMIN_IDS`) can:

- Receive payment notifications with proof images
- Approve or reject payments with inline buttons
- View user information and subscription details

## Database Schema

The bot uses the following tables:

- **users**: User profiles and subscription status
- **subscription_plans**: Available subscription plans
- **payments**: Payment records and approval status
- **file_conversions**: Conversion history and statistics
- **user_stats**: Daily usage statistics

## Supported Conversions

### Documents
- PDF ↔ DOCX, TXT, JPG, PNG
- DOCX ↔ PDF, TXT
- PPTX → PDF
- XLSX ↔ CSV

### Images
- JPG ↔ PNG ↔ WEBP ↔ BMP
- SVG → PNG, JPG
- Any image → PDF

### Audio (requires FFmpeg)
- MP3 ↔ WAV ↔ AAC ↔ OGG ↔ FLAC

### Video (requires FFmpeg)
- MP4 ↔ MKV ↔ AVI ↔ MOV
- Video → GIF

### Data
- JSON ↔ CSV ↔ XML
- Markdown → HTML, PDF

## Troubleshooting

### Common Issues

**"Conversion failed" errors:**
- Ensure all system dependencies are installed (ffmpeg, imagemagick, etc.)
- Check file permissions in `/tmp` directory
- Verify file format is actually supported

**Database connection errors:**
- Verify Supabase URL and key in `.env`
- Check internet connection
- Ensure database tables are created

**Bot not responding:**
- Verify bot token is correct
- Check if bot is running: `ps aux | grep bot.py`
- Review logs for error messages

### Logs

The bot logs all activities to stdout. To save logs:

```bash
python bot.py >> bot.log 2>&1
```

## Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/converter-bot.service`:

```ini
[Unit]
Description=Telegram File Converter Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/bot
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=/usr/bin/python3 /path/to/bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable converter-bot
sudo systemctl start converter-bot
sudo systemctl status converter-bot
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg imagemagick libreoffice pandoc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "bot.py"]
```

Build and run:
```bash
docker build -t converter-bot .
docker run -d --env-file .env converter-bot
```

## Security Considerations

- Never commit `.env` file to version control
- Use environment variables for all sensitive data
- Regularly update dependencies
- Implement rate limiting for production
- Use HTTPS for webhook mode (optional)
- Validate file types before conversion
- Set appropriate file size limits

## Performance Tips

- Use webhook mode instead of polling for production
- Implement file caching for repeated conversions
- Clean up temporary files regularly
- Use Redis for session management (optional)
- Implement job queue for heavy conversions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use for personal or commercial projects.

## Support

For support or questions:
- Telegram: @SimpleLearn_main_admin
- Issues: Create a GitHub issue

## Acknowledgments

- python-telegram-bot library
- Supabase for database
- FFmpeg for media conversion
- ImageMagick for image processing
- LibreOffice for document conversion