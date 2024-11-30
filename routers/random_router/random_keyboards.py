from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types


def message_random():
    kb_list = [
        [InlineKeyboardButton(text="получить предсказание", callback_data="random_inline")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list, resize_keyboard=True)
    return kb
