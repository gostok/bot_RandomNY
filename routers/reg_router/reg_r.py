from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from datetime import datetime

from routers.random_router.random_keyboards import message_random
from database.db import UserDatabase
from config.create_bot import bot

reg_router = Router()

db = UserDatabase()

CHANNEL_USERNAME = '@cityparkgrad'


class RegState(StatesGroup):
    user_id_state = State()
    date_of_birth_state = State()




@reg_router.callback_query(F.data.startswith("reg_inline"), StateFilter(RegState.user_id_state))
async def reg_cmd(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer()
    try:
        chat_member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)

        if chat_member.status in ['member', 'administrator', 'creator']:
            await callback.message.answer(
                'Теперь введи свою дату рождения (например, 03.10.1995), чтобы узнать будущее 🔮')
            await state.set_state(RegState.date_of_birth_state)
        else:
            await callback.message.answer("Пожалуйста, подпишитесь на канал, чтобы продолжить.")
    except Exception as e:
        await callback.message.answer("Не удалось проверить подписку. Убедитесь, что я имею доступ к каналу.")


@reg_router.message(StateFilter(RegState.date_of_birth_state))
async def reg_dob_cmd(message: types.Message, state: FSMContext):
    date_of_birth = message.text
    user_id = message.from_user.id
    try:
        # Проверка формата даты
        datetime.strptime(date_of_birth, '%d.%m.%Y')  # Проверяем, что дата в правильном формате
        db.add_user(user_id=user_id, birth_date=date_of_birth)
        await message.answer(f"Ого, кажется, именно тебе повезет в этом году 😉", reply_markup=message_random())
        await state.clear()
    except ValueError:
        await message.answer('Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ.')
    except Exception as e:
        await message.answer('Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз.')
        print(f"Ошибка при добавлении пользователя: {e}")
