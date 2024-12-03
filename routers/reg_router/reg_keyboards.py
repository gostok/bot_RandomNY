from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types


def reg_kb():
    kb_list = [
        [InlineKeyboardButton(text='Проверить подписку', callback_data='reg_inline')]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list, resize_keyboard=True)
    return kb

