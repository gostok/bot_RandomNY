from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from routers.reg_router.reg_keyboards import reg_kb
from routers.reg_router.reg_r import RegState
from routers.random_router.random_keyboards import message_random
from database.db import UserDatabase


start_router = Router()

db = UserDatabase()

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
        await message.answer('рег текст', reply_markup=reg_kb())
        await state.set_state(RegState.user_id_state)


@start_router.message(Command('user_count'))
async def cmd_start_uc(message: types.Message):
    user_count = db.get_user_count()
    await message.answer(f"Количество пользователей в базе данных: {user_count}")
