from aiogram_dialog import DialogManager
from services.api import api_service
from utils.localization import localization
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import config

logger = config.LOGGER.get_logger(__name__)

async def check_user(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Проверяет пользователя и возвращает данные для отображения.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, Any]: Словарь с данными пользователя и локализованными строками.
    """
    try:
        user = dialog_manager.event.from_user
        telegram_id: int = user.id
        username: str = user.username or user.full_name
        password: str = f"todo_Telegram_{telegram_id}"

        logger.info(f"Проверка пользователя: {username} (ID: {telegram_id})")
        user_info: Optional[Dict[str, Any]] = await api_service.get_user_info(telegram_id)
        if not user_info:
            logger.info(f"Создание нового пользователя: {username} (ID: {telegram_id})")
            user_info = await api_service.create_user(telegram_id, username, password)

        if user_info:
            locale: str = await localization.get_user_locale(telegram_id)
            user_token, user_id = await api_service.user_login(username, password)
            if user_token:
                logger.info(f"Пользователь {username} (ID: {telegram_id}) успешно авторизован")
                dialog_manager.dialog_data["user_token"] = user_token
                return {
                    "user": user_info,
                    "locale": locale,
                    "main_menu": localization.get_text("main_menu", locale),
                    "my_tasks": localization.get_text("my_tasks", locale),
                    "categories": localization.get_text("categories", locale),
                    "create_task": localization.get_text("create_task", locale),
                    "back": localization.get_text("back", locale),
                    "task_details": localization.get_text("task_details", locale),
                    "comments": localization.get_text("comments", locale),
                    "create_comment": localization.get_text("create_comment", locale),
                    "enter_task_name": localization.get_text("enter_task_name", locale),
                    "enter_task_description": localization.get_text("enter_task_description", locale),
                    "enter_task_due_date": localization.get_text("enter_task_due_date", locale),
                    "enter_task_categories": localization.get_text("enter_task_categories", locale),
                    "enter_category_name": localization.get_text("enter_category_name", locale),
                    "enter_comment_text": localization.get_text("enter_comment_text", locale),
                }
        logger.error(f"Ошибка при создании/авторизации пользователя: {username} (ID: {telegram_id})")
        return {"error": localization.get_text("error_user_creation", locale)}
    except Exception as e:
        logger.log_exception(f"Ошибка при проверке пользователя: {e}")
        return {"error": "Произошла ошибка при проверке пользователя"}

async def get_tasks(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Получает список задач пользователя.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, Any]: Словарь с задачами и локализованными строками.
    """
    try:
        user_token: str = dialog_manager.dialog_data.get("user_token")
        logger.info("Получение списка задач")
        tasks: List[Dict[str, Any]] = await api_service.get_tasks(user_token)
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        logger.info(f"Получено {len(tasks)} задач")
        return {
            "tasks": tasks,
            "create_task": localization.get_text("create_task", locale),
            "no_tasks": localization.get_text("no_tasks", locale),
            "my_tasks": localization.get_text("my_tasks", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при получении списка задач: {e}")

async def get_task_details(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Получает детали выбранной задачи.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, Any]: Словарь с деталями задачи и локализованными строками.
    """
    try:
        user_token: str = dialog_manager.dialog_data.get("user_token")
        task_id: str = dialog_manager.dialog_data.get("selected_task_id")
        locale: str = dialog_manager.dialog_data.get("locale", "ru")

        logger.info(f"Получение деталей задачи с ID: {task_id}")

        task: Dict[str, Any] = await api_service.get_task(user_token, task_id)

        if task['due_date']:
            due_date: datetime = datetime.fromisoformat(task['due_date'])
            task['due_date'] = due_date.strftime('%d.%m.%Y')

        categories: List[Dict[str, str]] = task.get('categories', [])
        categories_names: str = ", ".join([category['name'] for category in categories])
        logger.info(f"Детали задачи с ID {task_id} успешно получены")
        return {
            "task": task,
            "categories": categories_names,
            "assign_categories_title": localization.get_text("assign_categories_title", locale),
            "update_task_emoji": localization.get_text("update_task_emoji", locale),
            "complete_and_delete_task_emoji": localization.get_text("complete_and_delete_task_emoji", locale),
            "task_details": localization.get_text("task_details", locale),
            "task_description": localization.get_text("task_description", locale),
            "task_due_date": localization.get_text("task_due_date", locale),
            "task_categories": localization.get_text("categories", locale),
            "comments": localization.get_text("comments", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при получении деталей задачи: {e}")

async def get_categories(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Получает список категорий пользователя.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, Any]: Словарь с категориями и локализованными строками.
    """
    try:
        user_token: str = dialog_manager.dialog_data.get("user_token")
        logger.info("Получение списка категорий")
        categories: List[Dict[str, Any]] = await api_service.get_categories(user_token)
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        for category in categories:
            category["delete_category"] = localization.get_text("delete_category", locale)

        formatted_categories: str = "\n\n".join([
            f"Категория: {category['name']}\n"
            for category in categories
        ])
        logger.info(f"Получено {len(categories)} категорий")
        return {
            "categories": categories,
            "categories_format": formatted_categories,
            "no_categories": localization.get_text("no_categories", locale),
            "categories_title": localization.get_text("categories", locale),
            "create_category": localization.get_text("create_category", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при получении списка категорий: {e}")

async def get_categories_for_assignment(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Получает список категорий для назначения задаче.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, Any]: Словарь с категориями и локализованными строками.
    """
    try:
        user_token: str = dialog_manager.dialog_data.get("user_token")
        categories: List[Dict[str, Any]] = await api_service.get_categories(user_token)
        logger.info("Получение категорий для назначения")
        locale: str = dialog_manager.dialog_data.get("locale", "ru")

        dialog_manager.dialog_data["all_categories"] = categories
        logger.info(f"Получено {len(categories)} категорий для назначения")

        return {
            "categories": categories,
            "assign_categories_title": localization.get_text("assign_categories_title", locale),
            "save": localization.get_text("save", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        ...

async def get_comments(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Получает список комментариев для выбранной задачи.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, Any]: Словарь с комментариями и локализованными строками.
    """
    try:
        user_token: str = dialog_manager.dialog_data.get("user_token")
        task_id: str = dialog_manager.dialog_data.get("selected_task_id")
        logger.info(f"Получение комментариев для задачи с ID: {task_id}")
        comments: List[Dict[str, Any]] = await api_service.get_comments(user_token, task_id)
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        for comment in comments:
            comment["delete_comment"] = localization.get_text("delete_comment", locale)

        logger.info(f"Получено {len(comments)} комментариев")
        formatted_comments: str = "\n\n".join([
            f"ID: {comment['id']}\n"
            f"Содержание: {comment['content']}"
            for comment in comments
        ])

        return {
            "comments": formatted_comments,
            "comments_list": comments,
            "no_comments": localization.get_text("no_comments", locale),
            "comments_title": localization.get_text("comments", locale),
            "create_comment": localization.get_text("create_comment", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при получении комментариев: {e}")

async def get_create_comment(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    """
    Получает локализованные строки для создания комментария.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, str]: Словарь с локализованными строками.
    """
    try:
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        logger.info("Подготовка к созданию комментария")
        return {
            "create_comment": localization.get_text("create_comment", locale),
            "enter_comment_text": localization.get_text("enter_comment_text", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при подготовке к созданию комментария: {e}")

async def get_create_category(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    """
    Получает локализованные строки для создания категории.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, str]: Словарь с локализованными строками.
    """
    try:
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        logger.info("Подготовка к созданию категории")
        return {
            "create_category": localization.get_text("create_category", locale),
            "enter_category_name": localization.get_text("enter_category_name", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при подготовке к созданию категории: {e}")

async def get_create_task(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    """
    Получает локализованные строки для создания задачи.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, str]: Словарь с локализованными строками.
    """
    try:
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        logger.info("Подготовка к созданию задачи")
        return {
            "create_task": localization.get_text("create_task", locale),
            "enter_task_name": localization.get_text("enter_task_name", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при подготовке к созданию задачи: {e}")

async def get_task_description(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    """
    Получает локализованные строки для ввода описания задачи.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, str]: Словарь с локализованными строками.
    """
    try:
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        logger.info("Подготовка к вводу описания задачи")
        return {
            "enter_task_description": localization.get_text("enter_task_description", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при подготовке к вводу описания задачи: {e}")

async def get_task_due_date(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    """
    Получает локализованные строки для ввода срока выполнения задачи.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, str]: Словарь с локализованными строками.
    """
    try:
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        logger.info("Подготовка к вводу срока выполнения задачи")
        return {
            "enter_task_due_date": localization.get_text("enter_task_due_date", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при подготовке к вводу срока выполнения задачи: {e}")

async def get_task_categories(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    """
    Получает локализованные строки для ввода категорий задачи.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, str]: Словарь с локализованными строками.
    """
    try:
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        logger.info("Подготовка к вводу категорий задачи")
        return {
            "enter_task_categories": localization.get_text("enter_task_categories", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при подготовке к вводу категорий задачи: {e}")

async def get_update_title(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    """
    Получает локализованные строки для обновления заголовка задачи.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, str]: Словарь с локализованными строками.
    """
    try:
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        logger.info("Подготовка к обновлению заголовка задачи")
        return {
            "enter_new_title": localization.get_text("enter_new_title", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при подготовке к обновлению заголовка задачи: {e}")

async def get_update_description(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    """
    Получает локализованные строки для обновления описания задачи.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, str]: Словарь с локализованными строками.
    """
    try:
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        logger.info("Подготовка к обновлению описания задачи")
        return {
            "enter_new_description": localization.get_text("enter_new_description", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при подготовке к обновлению описания задачи: {e}")

async def get_update_due_date(dialog_manager: DialogManager, **kwargs) -> Dict[str, str]:
    """
    Получает локализованные строки для обновления срока выполнения задачи.

    Args:
        dialog_manager (DialogManager): Менеджер диалога.
        **kwargs: Дополнительные аргументы.

    Returns:
        Dict[str, str]: Словарь с локализованными строками.
    """
    try:
        locale: str = dialog_manager.dialog_data.get("locale", "ru")
        logger.info("Подготовка к обновлению срока выполнения задачи")
        return {
            "enter_new_due_date": localization.get_text("enter_new_due_date", locale),
            "back": localization.get_text("back", locale),
        }
    except Exception as e:
        logger.log_exception(f"Ошибка при подготовке к обновлению срока выполнения задачи: {e}")