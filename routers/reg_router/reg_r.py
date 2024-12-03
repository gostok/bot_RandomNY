from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from datetime import datetime

from routers.random_router.random_keyboards import message_random
from database.db import UserDatabase

reg_router = Router()

db = UserDatabase()


class RegState(StatesGroup):
    user_id_state = State()
    date_of_birth_state = State()




@reg_router.callback_query(F.data.startswith("reg_inline"), StateFilter(RegState.user_id_state))
async def reg_cmd(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Теперь введи свою дату рождения (например, 03.10.1995), чтобы узнать будущее! ')
    await state.set_state(RegState.date_of_birth_state)


@reg_router.message(StateFilter(RegState.date_of_birth_state))
async def reg_dob_cmd(message: types.Message, state: FSMContext):
    date_of_birth = message.text
    user_id = message.from_user.id
    try:
        # Проверка формата даты
        datetime.strptime(date_of_birth, '%d.%m.%Y')  # Проверяем, что дата в правильном формате
        db.add_user(user_id=user_id, birth_date=date_of_birth)
        await message.answer(f"Привет, @{message.from_user.username}.\n"
                             f"Я даю персональное новогоднее предсказание на каждый день при помощи мема.\n\n"
                             f"Начнем?", reply_markup=message_random())
        await state.clear()
    except ValueError:
        await message.answer('Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ.')
    except Exception as e:
        await message.answer('Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз.')
        print(f"Ошибка при добавлении пользователя: {e}")
