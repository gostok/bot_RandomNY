from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from routers.reg_router.reg_keyboards import reg_kb
from routers.reg_router.reg_r import RegState
from routers.random_router.random_keyboards import message_random
from database.db import UserDatabase
from config.create_bot import bot, CHAT_ADMIN
from config.booking import start_msg

start_router = Router()

db = UserDatabase()


class AdPost(StatesGroup):
    awaiting_ad_photo_state = State()


@start_router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user = db.get_user(user_id=user_id)
    if user is not None:
        await message.answer(f"Привет, @{message.from_user.username}.\n"
                             f"Я даю персональное новогоднее предсказание на каждый день при помощи мема.\n\n"
                             f"Начнем?", reply_markup=message_random())
    else:
        await message.answer(start_msg, reply_markup=reg_kb())
        await state.set_state(RegState.user_id_state)


@start_router.message(Command('user_count'))
async def cmd_start_uc(message: types.Message):
    user_count = db.get_user_count()
    await message.answer(f"Количество пользователей в базе данных: {user_count}")


@start_router.message(Command('ad_post'))
async def cmd_ad_post(message: types.Message, state: FSMContext):
    if message.chat.id != CHAT_ADMIN:
        await message.answer("Эта команда доступна только в группе администраторов.")
        return

    await message.answer("Введите текст(фото) рекламы или поста, который вы хотите отправить всем пользователям:")
    await state.set_state(AdPost.awaiting_ad_photo_state)


@start_router.message(StateFilter(AdPost.awaiting_ad_photo_state))
async def process_ad_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id if message.photo else None  # Проверяем, есть ли фото
    ad_text = message.text
    users = db.cursor.execute('SELECT user_id FROM users').fetchall()

    for user in users:
        user_id = user[0]
        try:
            if photo:
                await bot.send_photo(user_id, photo=photo)
            elif ad_text:
                await bot.send_message(user_id, ad_text)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    await message.answer("Реклама успешно отправлена всем пользователям.")
    await state.clear()
