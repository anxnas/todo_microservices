from django.utils import timezone
from django.conf import settings
from django.db import connection
from django.db.utils import ProgrammingError
from background_task import background
from typing import List, Optional, Dict, Any
import os
import requests
from tasks.models import Task

# Инициализация логгера
logger = settings.LOGGER.get_logger('task_management')

def get_auth_token() -> str:
    """
    Получает токен авторизации для Django проекта.

    Returns:
        str: Токен авторизации.

    Raises:
        ValueError: Если авторизация не удалась.
    """
    from django.contrib.auth import authenticate
    from django.contrib.auth.models import User
    from rest_framework_simplejwt.tokens import RefreshToken
    username: Optional[str] = os.getenv("API_USERNAME_TODO")
    password: Optional[str] = os.getenv("API_PASSWORD_TODO")

    if not username or not password:
        raise ValueError("Отсутствуют учетные данные для авторизации")

    user: Optional[User] = authenticate(username=username, password=password)
    if user is not None:
        refresh: RefreshToken = RefreshToken.for_user(user)
        return str(refresh.access_token)
    else:
        raise ValueError("Неверные учетные данные")

@background(schedule=settings.TIME_COMPLETED_TASK_INTERVAL)
def delete_completed_tasks() -> None:
    """
    Удаляет все выполненные задачи и связанные с ними комментарии.

    Эта функция проверяет настройку TIME_COMPLETED_TASK в settings.py.
    Если она включена, функция удаляет все задачи, помеченные как выполненные,
    а также удаляет связанные с ними комментарии в микросервисе комментариев.

    Raises:
        Exception: Если произошла ошибка при удалении задач или комментариев.
    """
    if settings.TIME_COMPLETED_TASK:
        try:
            completed_tasks: List[Task] = list(Task.objects.filter(completed=True))
            count: int = len(completed_tasks)
            for task in completed_tasks:
                delete_task_comments(task.id)
                task.delete()
            logger.info(f"Удалено {count} выполненных задач и связанных комментариев.")
        except Exception as e:
            logger.log_exception(f"Ошибка при удалении выполненных задач: {str(e)}")

@background(schedule=settings.TIME_DUE_TASK_INTERVAL)
def mark_overdue_tasks() -> None:
    """
    Отмечает и удаляет все просроченные задачи и связанные с ними комментарии.

    Эта функция проверяет настройку TIME_DUE_TASK в settings.py.
    Если она включена, функция отмечает все невыполненные задачи,
    у которых прошел срок выполнения, как "Просрочено", а затем удаляет их
    вместе со связанными комментариями.

    Raises:
        Exception: Если произошла ошибка при обработке задач или комментариев.
    """
    if settings.TIME_DUE_TASK:
        try:
            now: timezone.datetime = timezone.now()
            overdue_tasks: List[Task] = list(Task.objects.filter(due_date__lt=now, completed=False))
            count: int = len(overdue_tasks)
            for task in overdue_tasks:
                task.status = 'Просрочено'
                logger.info(f"Задача '{task.title}' (ID: {task.id}) помечена как просроченная и будет удалена.")
                delete_task_comments(task.id)
                task.delete()
            logger.info(f"Обработано и удалено {count} просроченных задач и связанных комментариев.")
        except Exception as e:
            logger.log_exception(f"Ошибка при обработке просроченных задач: {str(e)}")

def delete_task_comments(task_id: str) -> None:
    """
    Удаляет все комментарии, связанные с заданной задачей, в микросервисе комментариев.

    Args:
        task_id (str): ID задачи, для которой нужно удалить комментарии.

    Raises:
        Exception: Если произошла ошибка при удалении комментариев.
    """
    try:
        # Получаем токен авторизации для Django проекта
        token: str = get_auth_token()

        headers: Dict[str, str] = {"Authorization": f"Bearer {token}"}

        # Получаем все комментарии для задачи
        response: requests.Response = requests.get(f"{settings.COMMENTS_SERVICE_URL}/tasks/{task_id}/comments", headers=headers)
        response.raise_for_status()
        comments: List[Dict[str, Any]] = response.json()

        # Удаляем каждый комментарий по отдельности
        for comment in comments:
            comment_id: int = comment['id']
            delete_response: requests.Response = requests.delete(f"{settings.COMMENTS_SERVICE_URL}/comments/{comment_id}", headers=headers)
            delete_response.raise_for_status()
            logger.info(f"Комментарий с ID {comment_id} для задачи {task_id} успешно удален.")

        logger.info(f"Все комментарии для задачи с ID {task_id} успешно удалены.")
    except requests.RequestException as e:
        logger.log_exception(f"Ошибка при удалении комментариев для задачи с ID {task_id}: {str(e)}")
    except ValueError as e:
        logger.log_exception(f"Ошибка авторизации: {str(e)}")
    except Exception as e:
        logger.log_exception(f"Неожиданная ошибка при удалении комментариев для задачи с ID {task_id}: {str(e)}")


def initialize_background_tasks() -> None:
    """
    Инициализирует фоновые задачи.

    Эта функция запускает фоновые задачи для удаления выполненных задач
    и отметки просроченных задач с интервалами, указанными в settings.py.
    """
    logger.info("Начало инициализации фоновых задач.")

    # Проверяем, существует ли таблица background_task
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM background_task LIMIT 1")
    except ProgrammingError:
        logger.warning("Таблица background_task не существует. Пропускаем инициализацию фоновых задач.")
        return

    from background_task.models import Task

    # Удаляем все существующие задачи с теми же именами
    Task.objects.filter(task_name__in=['tasks.task_management.delete_completed_tasks',
                                       'tasks.task_management.mark_overdue_tasks']).delete()

    delete_completed_tasks(repeat=settings.TIME_COMPLETED_TASK_INTERVAL)
    mark_overdue_tasks(repeat=settings.TIME_DUE_TASK_INTERVAL)
    logger.info("Фоновые задачи успешно инициализированы.")