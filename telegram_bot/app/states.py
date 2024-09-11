from aiogram.filters.state import StatesGroup, State
from config import config

logger = config.LOGGER.get_logger(__name__)

class MainSG(StatesGroup):
    """
    Определяет состояния для основного диалога.

    Attributes:
        language_select (State): Состояние выбора языка.
        main (State): Главное состояние.
        tasks (State): Состояние списка задач.
        create_task (State): Состояние создания задачи.
        create_task_description (State): Состояние добавления описания задачи.
        create_task_due_date (State): Состояние добавления срока выполнения задачи.
        create_task_categories (State): Состояние добавления категорий задачи.
        task_details (State): Состояние просмотра деталей задачи.
        categories (State): Состояние списка категорий.
        create_category (State): Состояние создания категории.
        comments (State): Состояние списка комментариев.
        create_comment (State): Состояние создания комментария.
        assign_categories (State): Состояние назначения категорий.
        update_task (State): Состояние обновления задачи.
        complete_and_delete_task (State): Состояние завершения и удаления задачи.
        update_task_title (State): Состояние обновления заголовка задачи.
        update_task_description (State): Состояние обновления описания задачи.
        update_task_due_date (State): Состояние обновления срока выполнения задачи.
    """
    language_select = State()
    main = State()
    tasks = State()
    create_task = State()
    create_task_description = State()
    create_task_due_date = State()
    create_task_categories = State()
    task_details = State()
    categories = State()
    create_category = State()
    comments = State()
    create_comment = State()
    assign_categories = State()
    update_task = State()
    complete_and_delete_task = State()
    update_task_title = State()
    update_task_description = State()
    update_task_due_date = State()

try:
    # Пример использования логгера
    logger.info("Инициализация состояний MainSG завершена успешно.")
except Exception as e:
    logger.log_exception("Ошибка при инициализации состояний MainSG")