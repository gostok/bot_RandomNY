import os
import random
import logging
import asyncio
from datetime import datetime
from aiogram import Router, F, types
from aiogram.types.input_file import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.context import FSMContext

from database.db import UserDatabase
from config.create_bot import bot


logging.basicConfig(level=logging.INFO)

random_router = Router()

db = UserDatabase()
scheduler = AsyncIOScheduler()

IMAGES_DIR = 'database/images'

async def send_random_image(user_id):
    images = [img for img in os.listdir(IMAGES_DIR) if img.endswith(('.png', '.jpg', '.jpeg'))]

    if not images:
        print("Нет доступных изображений для отправки.")
        return

    random_image = random.choice(images)
    image_path = os.path.join(IMAGES_DIR, random_image)

    photo = FSInputFile(image_path)

    await bot.send_photo(user_id, photo, caption='Новогоднее предсказание на сегодня')
    return image_path


@random_router.callback_query(F.data.startswith('random_inline'))
async def random_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    await callback.answer()

    if user is not None:
        last_prediction = db.get_last_prediction(user_id=user_id)
        today = datetime.now().date().isoformat()  # Получаем текущую дату в формате ISO



        if last_prediction is not None and last_prediction[1] == today:  # Проверяем, существует ли предсказание
            if os.path.exists(last_prediction[0]):
                photo = FSInputFile(last_prediction[0])  # Используем FSInputFile для локального файла
                await bot.send_photo(user_id, photo, caption='Новогоднее предсказание на сегодня')
            else:
                logging.error(f"Файл не найден: {last_prediction[0]}")
        else:
            # Отправляем сообщение о поиске предсказания
            processing_message = await callback.message.answer("Ищу для тебя предсказание...")
            await asyncio.sleep(1)
            await bot.delete_message(
                user_id, message_id=processing_message.message_id
            )
            processing_message = await callback.message.answer("Что-то нахожу...")
            await asyncio.sleep(1)
            await bot.delete_message(
                user_id, message_id=processing_message.message_id
            )
            processing_message = await callback.message.answer("Нашел...")
            await asyncio.sleep(1)
            await bot.delete_message(
                user_id, message_id=processing_message.message_id
            )

            image_path = await send_random_image(user_id)  # Отправляем случайное изображение
            if image_path:  # Проверяем, что изображение было успешно отправлено
                db.update_last_prediction(user_id, image_path)  # Обновляем последнее предсказание

        # Запланируем отправку случайного изображения каждый день в 10:00
        scheduler.add_job(send_random_image, 'cron', args=[user_id], hour=10, minute=0, timezone='Europe/Moscow')
        if not scheduler.running:
            scheduler.start()  # Запускаем планировщик, если он еще не запущен
    else:
        logging.info('Ошибка отправки рандом сообщения: пользователь не найден.')

