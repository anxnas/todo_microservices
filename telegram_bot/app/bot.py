from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs, StartMode
from config import config
from dialogs import main_dialog, MainSG
from services.api import api_service
from utils.localization import localization

logger = config.LOGGER.get_logger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

@router.message(Command("start"))
async def start_command(message, dialog_manager):
    """
    Обработчик команды /start.

    Проверяет наличие локали пользователя и запускает соответствующий диалог.

    Args:
        message: Объект сообщения от пользователя.
        dialog_manager: Менеджер диалогов для управления состояниями.

    Returns:
        None
    """
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запустил команду /start")
    locale = await localization.get_user_locale(user_id)
    if locale:
        logger.info(f"Запуск основного диалога для пользователя {user_id}")
        await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)
    else:
        logger.info(f"Запуск диалога выбора языка для пользователя {user_id}")
        await dialog_manager.start(MainSG.language_select, mode=StartMode.RESET_STACK)

def register_dialogs():
    """
    Регистрирует диалоги и маршрутизаторы в диспетчере.

    Returns:
        None
    """
    logger.info("Регистрация диалогов и маршрутизаторов")
    setup_dialogs(dp)
    dp.include_router(main_dialog)
    dp.include_router(router)

async def on_startup():
    """
    Выполняется при запуске бота.

    Инициализирует сессию API, базу данных для локализации и регистрирует диалоги.

    Returns:
        None
    """
    logger.info("Запуск бота")
    try:
        await api_service.create_session()
        await localization.init_db()
        register_dialogs()
        logger.info("Бот успешно запущен")
    except Exception as e:
        logger.log_exception("Ошибка при запуске бота")

async def on_shutdown():
    """
    Выполняется при завершении работы бота.

    Закрывает сессию API.

    Returns:
        None
    """
    logger.info("Завершение работы бота")
    try:
        await api_service.close_session()
        logger.info("Сессия API успешно закрыта")
    except Exception as e:
        logger.log_exception("Ошибка при закрытии сессии API")

async def start_bot():
    """
    Запускает бота.

    Регистрирует функции запуска и завершения, затем запускает поллинг обновлений.

    Returns:
        None
    """
    logger.info("Начало запуска бота")
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.log_exception("Ошибка при запуске поллинга бота")

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())