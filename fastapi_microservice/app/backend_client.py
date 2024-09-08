import httpx
from typing import Optional, Dict, Any
from app.config import settings

logger = settings.LOGGER.get_logger('backend_client')

class BackendClientError(Exception):
    """Базовый класс для исключений в этом модуле."""
    pass

class TokenError(BackendClientError):
    """Исключение, вызываемое при проблемах с получением токена."""
    pass

class TaskError(BackendClientError):
    """Исключение, вызываемое при проблемах с задачами."""
    pass

class BackendClient:
    """Класс для взаимодействия с бэкендом Django."""

    def __init__(self) -> None:
        self.base_url: str = settings.DJANGO_BACKEND_URL
        self.username: str = settings.API_USERNAME_TODO
        self.password: str = settings.API_PASSWORD_TODO

    async def get_token(self) -> str:
        """
        Получает токен аутентификации от бэкенда.

        Returns:
            str: Токен доступа.

        Raises:
            TokenError: Если не удалось получить токен.
        """
        try:
            async with httpx.AsyncClient() as client:
                response: httpx.Response = await client.post(
                    f"{self.base_url}/api/token/",
                    data={"username": self.username, "password": self.password}
                )
                response.raise_for_status()
                token: str = response.json()["access"]
                logger.info("Токен успешно получен")
                return token
        except httpx.HTTPStatusError as e:
            logger.log_exception(f"Ошибка при получении токена: {e}")
        except Exception as e:
            logger.log_exception(f"Неожиданная ошибка при получении токена: {e}")

    async def check_task_exists(self, task_id: int) -> bool:
        """
        Проверяет существование задачи по её ID.

        Args:
            task_id (int): ID задачи для проверки.

        Returns:
            bool: True, если задача существует, иначе False.

        Raises:
            TaskError: Если произошла ошибка при проверке задачи.
        """
        try:
            token: str = await self.get_token()
            async with httpx.AsyncClient() as client:
                response: httpx.Response = await client.get(
                    f"{self.base_url}/api/tasks/{task_id}/",
                    headers={"Authorization": f"Bearer {token}"}
                )
                exists: bool = response.status_code == 200
                logger.info(f"Проверка существования задачи {task_id}: {'существует' if exists else 'не существует'}")
                return exists
        except TokenError as e:
            logger.log_exception(f"Ошибка токена при проверке задачи {task_id}: {e}")
        except Exception as e:
            logger.log_exception(f"Ошибка при проверке существования задачи {task_id}: {e}")

    async def get_task_details(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает детали задачи по её ID.

        Args:
            task_id (int): ID задачи.

        Returns:
            Optional[Dict[str, Any]]: Словарь с деталями задачи или None, если задача не найдена.

        Raises:
            TaskError: Если произошла ошибка при получении деталей задачи.
        """
        try:
            token: str = await self.get_token()
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
        except TokenError as e:
            logger.log_exception(f"Ошибка токена при получении деталей задачи {task_id}: {e}")
        except Exception as e:
            logger.log_exception(f"Неожиданная ошибка при получении деталей задачи {task_id}: {e}")