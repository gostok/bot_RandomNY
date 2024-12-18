from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from routers.reg_router.reg_keyboards import reg_kb
from routers.reg_router.reg_r import RegState
from routers.random_router.random_keyboards import message_random
from database.db import UserDatabase
from config.create_bot import bot, CHAT_ADMIN, ADMIN
from config.booking import start_msg, admin_msg

start_router = Router()

db = UserDatabase()


class AdPost(StatesGroup):
    awaiting_ad_photo_state = State()


def is_admin(user_id):
    return user_id == int(CHAT_ADMIN) or user_id == int(ADMIN)  # Проверяем, является ли пользователь администратором


@start_router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user = db.get_user(user_id=user_id)
    if user is not None:
        await message.answer(f"Ого, кажется, именно тебе повезет в этом году 😉\n"
                             , reply_markup=message_random())
    else:
        await message.answer(start_msg, reply_markup=reg_kb())
        await state.set_state(RegState.user_id_state)


@start_router.message(Command('admin'))
async def cmd_start_uc(message: types.Message):
    user = message.from_user.id
    if not is_admin(user):
        await message.answer("Эта команда доступна только для администратора.")
        return
    await message.answer(admin_msg)


@start_router.message(Command('user_count'))
async def cmd_start_uc(message: types.Message):
    user = message.from_user.id
    if not is_admin(user):
        await message.answer("Эта команда доступна только для администратора.")
        return

    user_count = db.get_user_count()
    await message.answer(f"Количество пользователей в базе данных: {user_count}")


@start_router.message(Command('ad_post'))
async def cmd_ad_post(message: types.Message, state: FSMContext):
    user = message.from_user.id
    if not is_admin(user):
        await message.answer("Эта команда доступна только для администратора.")
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
