import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from config import BOT_TOKEN
from handlers import register_handlers
from utils.i18n import i18n_middleware


async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Настройка middleware для i18n
    dp.message.middleware(i18n_middleware)
    dp.callback_query.middleware(i18n_middleware)

    # Регистрация обработчиков
    register_handlers(dp)

    # Настройка диалогов
    setup_dialogs(dp)

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())