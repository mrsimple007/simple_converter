
from datetime import datetime, timezone  
import os
import logging
import asyncio

logging.getLogger("httpx").setLevel(logging.WARNING)

# Configuration
# BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN_SIMPLELEARNINGUZ")


CARD_NUMBER = "4073 4200 3711 6443"
ADMIN_CHAT_ID = "8437026582"
ADMIN_USERNAME="@SimpleLearn_main_admin"
NOTIFICATION_ADMIN_IDS = ["8437026582", "999932510"]

# INSTAGRAM_ADMIN_IDS = [7967610894, 
#                        8437026582, 
#                        122290051, 
#                        999932510, 
#                        8126290272]


# FREEMIUM LIMITS
FREE_TIER_LIMITS = {
    'daily_conversions': 30,  # 30 conversions per day for free users
    'max_file_size_mb': 50,   # 50 MB max file size
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