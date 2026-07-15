"""
Logging module for the Telegram Shop Bot.
Configures logging for console and file output.
"""

import logging
import logging.handlers
from config import LOG_LEVEL, LOG_FILE

# Create logger
logger = logging.getLogger('shop_bot')
logger.setLevel(LOG_LEVEL)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(formatter)

# File handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=10485760,  # 10MB
    backupCount=5
)
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Suppress aiogram debug logs
logging.getLogger('aiogram').setLevel(logging.WARNING)
