import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
ADMIN = os.getenv('ADMIN')
CHAT_ADMIN = os.getenv('CHAT_ADMIN')


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
