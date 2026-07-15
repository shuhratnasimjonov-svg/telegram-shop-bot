"""
Loader module for the Telegram Shop Bot.
Initializes bot, dispatcher, and storage for FSM.
"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from logger import logger

# Initialize bot
bot = Bot(token=BOT_TOKEN)

# Initialize storage for FSM (Finite State Machine)
storage = MemoryStorage()

# Initialize dispatcher
dp = Dispatcher(storage=storage)

logger.info("✓ Bot, Dispatcher, and Storage initialized successfully")
