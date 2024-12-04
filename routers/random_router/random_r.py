import os
import random
import logging
import asyncio
from datetime import datetime
from aiogram import Router, F, types
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command

from database.db import UserDatabase
from config.create_bot import bot


logging.basicConfig(level=logging.INFO)

random_router = Router()

db = UserDatabase()

IMAGES_DIR = 'database/images'


async def send_saved_image(user_id, image_path):
    if os.path.exists(image_path):
        photo = FSInputFile(image_path)
        await bot.send_photo(user_id, photo, caption='Ваш вайб на 2025 год')
    else:
        logging.warning(f"Изображение по пути {image_path} не найдено.")


async def handle_meme_request(user_id, message):
    user = db.get_user(user_id)

    if user is not None:
        last_prediction = db.get_last_prediction(user_id=user_id)
        logging.info(f"Last prediction: {last_prediction}")

        if last_prediction is None:
            images = [img for img in os.listdir(IMAGES_DIR) if img.endswith(('.png', '.jpg', '.jpeg'))]
            if not images:
                logging.warning("Нет доступных изображений для отправки.")
                return None

            random_image = random.choice(images)
            image_path = os.path.join(IMAGES_DIR, random_image)

            # Отправляем сообщение о процессе
            processing_messages = [
                "Направляю запрос во Вселенную мемов 🌌",
                "Устанавливаю связь с космосом 💫",
                "Ожидаю расклад от главного мемолога 🥠",
                "Загружаю мемологическую картотеку 🔮"
            ]

            for msg in processing_messages:
                processing_message = await message.answer(msg)
                await asyncio.sleep(1.5)
                await bot.delete_message(user_id, message_id=processing_message.message_id)

            await send_saved_image(user_id, image_path)
            db.update_last_prediction(user_id, image_path)
        else:
            # Проверяем, если last_prediction - это кортеж
            if isinstance(last_prediction, tuple):
                last_prediction = last_prediction[0]  # Измените это в зависимости от структуры вашего кортежа

            await send_saved_image(user_id, last_prediction)
    else:
        logging.info('Ошибка отправки рандом сообщения: пользователь не найден.')


@random_router.message(Command('meme'))  # Обработчик для команды /meme
async def meme_command_handler(message: types.Message):
    await handle_meme_request(message.from_user.id, message)


@random_router.callback_query(F.data.startswith("random_inline"))  # Обработчик для инлайн-кнопок
async def meme_button_handler(callback: types.CallbackQuery):
    await callback.answer()  # Подтверждаем нажатие кнопки
    await handle_meme_request(callback.from_user.id, callback.message)
