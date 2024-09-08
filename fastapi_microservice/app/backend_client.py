import httpx
from typing import Optional, Dict, Any
from app.config import settings

logger = settings.LOGGER.get_logger('backend_client')

class BackendClientError(Exception):
    """Базовый класс для исключений в этом модуле."""
    pass

class TaskError(BackendClientError):
    """Исключение, вызываемое при проблемах с задачами."""
    pass

class BackendClient:
    """Класс для взаимодействия с бэкендом Django."""

    def __init__(self) -> None:
        self.base_url: str = settings.DJANGO_BACKEND_URL

    async def check_task_exists(self, token: str, task_id: int) -> bool:
        """
        Проверяет существование задачи по её ID.

        Args:
            token (str): Токен доступа.
            task_id (int): ID задачи для проверки.

        Returns:
            bool: True, если задача существует, иначе False.

        Raises:
            TaskError: Если произошла ошибка при проверке задачи.
        """
        try:
            async with httpx.AsyncClient() as client:
                response: httpx.Response = await client.get(
                    f"{self.base_url}/api/tasks/{task_id}/",
                    headers={"Authorization": f"Bearer {token}"}
                )
                exists: bool = response.status_code == 200
                logger.info(f"Проверка существования задачи {task_id}: {'существует' if exists else 'не существует'}")
                return exists
        except Exception as e:
            logger.log_exception(f"Ошибка при проверке существования задачи {task_id}: {e}")
            raise TaskError(f"Ошибка при проверке существования задачи {task_id}: {e}")

    async def get_task_details(self, token: str, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает детали задачи по её ID.

        Args:
            token (str): Токен доступа.
            task_id (int): ID задачи.

        Returns:
            Optional[Dict[str, Any]]: Словарь с деталями задачи или None, если задача не найдена.

        Raises:
            TaskError: Если произошла ошибка при получении деталей задачи.
        """
        try:
            async with httpx.AsyncClient() as client:
                response: httpx.Response = await client.get(
                    f"{self.base_url}/api/tasks/{task_id}/",
                    headers={"Authorization": f"Bearer {token}"}
                )
                response.raise_for_status()
                task_details: Dict[str, Any] = response.json()
                logger.info(f"Получены детали задачи {task_id}")
                return task_details
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Задача {task_id} не найдена")
                return None
            logger.log_exception(f"Ошибка при получении деталей задачи {task_id}: {e}")
            raise TaskError(f"Ошибка при получении деталей задачи {task_id}: {e}")
        except Exception as e:
            logger.log_exception(f"Неожиданная ошибка при получении деталей задачи {task_id}: {e}")
            raise TaskError(f"Неожиданная ошибка при получении деталей задачи {task_id}: {e}")