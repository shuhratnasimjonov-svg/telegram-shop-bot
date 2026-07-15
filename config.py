"""
Configuration module for the Telegram Shop Bot.
Loads and manages all environment variables and settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Telegram Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

ADMIN_IDS = list(map(int, os.getenv('ADMIN_ID', '0').split(',')))

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/shop_bot.db')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# Ensure database directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# Channel Configuration for mandatory subscription
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@your_channel')
ENABLE_CHANNEL_SUB = os.getenv('ENABLE_CHANNEL_SUB', 'True').lower() == 'true'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'bot.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Multi-language Configuration
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')
SUPPORTED_LANGUAGES = ['en', 'ru', 'uz']

# Feature Flags
ENABLE_REFERRAL = os.getenv('ENABLE_REFERRAL', 'True').lower() == 'true'
ENABLE_PROMO = os.getenv('ENABLE_PROMO', 'True').lower() == 'true'

# Payment Configuration (Placeholder for future integration)
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN', '')

# Anti-spam and Rate Limiting Configuration
MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '30'))
SPAM_BAN_DURATION = 3600  # 1 hour in seconds

# Bot Settings
PRODUCTS_PER_PAGE = 5
CATEGORIES_PER_PAGE = 4
ORDERS_PER_PAGE = 5

# Referral System Configuration
REFERRAL_BONUS = 5000  # Bonus amount in smallest currency unit
REFERRAL_BONUS_PERCENTAGE = 5  # Percentage discount for referred friends

# Promo Code Configuration
MAX_DISCOUNT_PERCENTAGE = 50
MAX_DISCOUNT_AMOUNT = 100000

# Contact Support Configuration
SUPPORT_CHAT_ID = int(os.getenv('ADMIN_ID', '0'))

# API Request Timeouts
REQUEST_TIMEOUT = 30

# Pagination settings
INLINE_KEYBOARD_BUTTON_WIDTH = 2

# Cache settings (in seconds)
CACHE_TTL = 3600

print(f"✓ Configuration loaded successfully")
print(f"✓ Bot Token configured")
print(f"✓ Database: {DATABASE_PATH}")
print(f"✓ Admin IDs: {ADMIN_IDS}")
print(f"✓ Channel subscription: {'Enabled' if ENABLE_CHANNEL_SUB else 'Disabled'}")
print(f"✓ Referral system: {'Enabled' if ENABLE_REFERRAL else 'Disabled'}")
print(f"✓ Promo codes: {'Enabled' if ENABLE_PROMO else 'Disabled'}")
