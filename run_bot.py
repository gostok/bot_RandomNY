import asyncio
from config.create_bot import bot, dp, ADMIN
import logging
from config.all_routers import all_routers

admin_id = ADMIN
logging.basicConfig(level=logging.INFO)



async def on_startup(dp):
    logging.info('Бот включился')
    try:
        await bot.send_message(admin_id, 'Бот включился')
    except Exception as exc:
        logging.error(f'Не удалось отправить сообщение админу: {exc}')


async def on_shutdown(dp):
    logging.info('Бот отключился')
    try:
        await bot.send_message(admin_id, 'Бот отключился')
    except Exception as exc:
        logging.error(f'Не удалось отправить сообщение админу: {exc}')


async def main():

    await on_startup(dp)
    await bot.delete_webhook(drop_pending_updates=True)

    for router in all_routers:
        dp.include_router(router)

    try:
        await dp.start_polling(bot, on_startup=on_startup, on_shutdown=on_shutdown)
    except Exception as exc:
        logging.error(f'Ошибка во время работы бота: {exc}')
        await on_shutdown(dp)


if __name__ == '__main__':
    print('Запуск бота...')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Бот останавливается...')
        asyncio.run(on_shutdown(dp))  # Уведомляем администратора об остановке
        print("Бот отключен.")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        asyncio.run(on_shutdown(dp)) # Уведомляем администратора об остановке
        