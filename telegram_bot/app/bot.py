from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs, StartMode
from config import config
from dialogs import main_dialog, MainSG
from services.api import api_service
from utils.localization import localization
import pretty_errors

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

@router.message(Command("start"))
async def start_command(message, dialog_manager):
    user_id = message.from_user.id
    locale = await localization.get_user_locale(user_id)
    if locale:
        await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(MainSG.language_select, mode=StartMode.RESET_STACK)

def register_dialogs():
    setup_dialogs(dp)
    dp.include_router(main_dialog)
    dp.include_router(router)

async def on_startup():
    await api_service.create_session()
    await localization.init_db()  # Добавьте эту строку
    register_dialogs()

async def on_shutdown():
    await api_service.close_session()

async def start_bot():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())