import aiohttp
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from config import config
from models.user import User

logger = config.LOGGER.get_logger(__name__)

class APIService:
    """
    Класс для взаимодействия с API сервера.

    Attributes:
        base_url (str): Базовый URL API.
        fastapi_url (str): URL FastAPI сервера.
        session (Optional[aiohttp.ClientSession]): Сессия для выполнения HTTP-запросов.
        admin_token (Optional[str]): Токен администратора для авторизации.
    """
    def __init__(self):
        """
        Инициализирует объект APIService.
        """
        self.base_url: str = config.API_BASE_URL
        self.fastapi_url: str = config.FASTAPI_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self.admin_token: Optional[str] = None
        logger.info("APIService инициализирован")

    async def create_session(self) -> None:
        """
        Создает сессию для HTTP-запросов и выполняет вход администратора.
        """
        self.session = aiohttp.ClientSession()
        while True:
            try:
                await self.admin_login(config.API_USERNAME_TODO, config.API_PASSWORD_TODO)
                logger.info("Успешный вход администратора")
                break  # Выход из цикла при успешном входе
            except Exception as e:
                logger.error(f"Ошибка при входе администратора: {e}")
                await asyncio.sleep(5)

    async def close_session(self) -> None:
        """
        Закрывает сессию HTTP-запросов.
        """
        if self.session:
            await self.session.close()
            logger.info("Сессия HTTP-запросов закрыта")

    async def admin_login(self, username: str, password: str) -> Optional[int]:
        """
        Выполняет вход администратора и сохраняет токен.

        Args:
            username (str): Имя пользователя администратора.
            password (str): Пароль администратора.

        Returns:
            Optional[int]: ID пользователя-администратора или None в случае ошибки.
        """
        async with self.session.post(f"{self.base_url}/token/", data={"username": username, "password": password}) as response:
            if response.status == 200:
                data: Dict[str, Any] = await response.json()
                self.admin_token = data["access"]
                logger.info(f"Администратор успешно вошел в систему. ID: {data['user_id']}")
                return data["user_id"]
            logger.error("Ошибка входа администратора")
            return None

    async def user_login(self, username: str, password: str) -> Tuple[Optional[str], Optional[int]]:
        """
        Выполняет вход пользователя.

        Args:
            username (str): Имя пользователя.
            password (str): Пароль пользователя.

        Returns:
            Tuple[Optional[str], Optional[int]]: Токен доступа и ID пользователя или (None, None) в случае ошибки.
        """
        async with self.session.post(f"{self.base_url}/token/", data={"username": username, "password": password}) as response:
            if response.status == 200:
                data: Dict[str, Any] = await response.json()
                logger.info(f"Пользователь {username} успешно вошел в систему. ID: {data['user_id']}")
                return data["access"], data["user_id"]
            logger.error(f"Ошибка входа пользователя {username}")
            return None, None

    async def get_user_info(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о пользователе по его Telegram ID.

        Args:
            telegram_id (int): Telegram ID пользователя.

        Returns:
            Optional[Dict[str, Any]]: Информация о пользователе или None в случае ошибки.
        """
        async with self.session.get(f"{self.base_url}/users/{telegram_id}/public_info/", headers=self.get_admin_headers()) as response:
            if response.status == 200:
                user_info = await response.json()
                logger.info(f"Получена информация о пользователе с Telegram ID: {telegram_id}")
                return user_info
            logger.error(f"Ошибка получения информации о пользователе с Telegram ID: {telegram_id}")
            return None

    async def create_user(self, telegram_id: int, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Создает нового пользователя.

        Args:
            telegram_id (int): Telegram ID пользователя.
            username (str): Имя пользователя.
            password (str): Пароль пользователя.

        Returns:
            Optional[Dict[str, Any]]: Информация о созданном пользователе или None в случае ошибки.
        """
        data: Dict[str, Any] = {
            "username": username,
            "password": password,
            "id": telegram_id
        }
        async with self.session.post(f"{self.base_url}/users/", json=data, headers=self.get_admin_headers()) as response:
            if response.status == 201:
                user_info = await response.json()
                logger.info(f"Создан новый пользователь: {username}")
                return user_info
            logger.error(f"Ошибка создания пользователя: {username}")
            return None

    async def get_task(self, user_token: str, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о задаче по её ID.

        Args:
            user_token (str): Токен пользователя.
            task_id (str): ID задачи.

        Returns:
            Optional[Dict[str, Any]]: Информация о задаче или None в случае ошибки.
        """
        async with self.session.get(f"{self.base_url}/tasks/{task_id}/",
                                    headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                task = await response.json()
                logger.info(f"Получена задача с ID: {task_id}")
                return task
            logger.error(f"Ошибка получения задачи с ID: {task_id}")
            return None

    async def get_tasks(self, user_token: str) -> List[Dict[str, Any]]:
        """
        Получает список всех задач пользователя.

        Args:
            user_token (str): Токен пользователя.

        Returns:
            List[Dict[str, Any]]: Список задач пользователя.
        """
        async with self.session.get(f"{self.base_url}/tasks/", headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                tasks = await response.json()
                logger.info(f"Получено {len(tasks)} задач")
                return tasks
            logger.error("Ошибка получения списка задач")
            return []

    async def create_task(self, user_token: str, title: str, description: str, due_date: str, categories: List[str]) -> Optional[Dict[str, Any]]:
        """
        Создает новую задачу.

        Args:
            user_token (str): Токен пользователя.
            title (str): Заголовок задачи.
            description (str): Описание задачи.
            due_date (str): Срок выполнения задачи.
            categories (List[str]): Список категорий задачи.

        Returns:
            Optional[Dict[str, Any]]: Информация о созданной задаче или None в случае ошибки.
        """
        data: Dict[str, Any] = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "categories": [{"name": cat} for cat in categories]
        }
        async with self.session.post(f"{self.base_url}/tasks/", json=data, headers=self.get_user_headers(user_token)) as response:
            if response.status == 201:
                task = await response.json()
                logger.info(f"Создана новая задача: {title}")
                return task
            logger.error(f"Ошибка создания задачи: {title}")
            return None

    async def get_categories(self, user_token: str) -> List[Dict[str, Any]]:
        """
        Получает список всех категорий пользователя.

        Args:
            user_token (str): Токен пользователя.

        Returns:
            List[Dict[str, Any]]: Список категорий пользователя.
        """
        async with self.session.get(f"{self.base_url}/categories/", headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                categories = await response.json()
                logger.info(f"Получено {len(categories)} категорий")
                return categories
            logger.error("Ошибка получения списка категорий")
            return []

    async def create_category(self, user_token: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Создает новую категорию.

        Args:
            user_token (str): Токен пользователя.
            name (str): Название категории.

        Returns:
            Optional[Dict[str, Any]]: Информация о созданной категории или None в случае ошибки.
        """
        data: Dict[str, str] = {"name": name}
        async with self.session.post(f"{self.base_url}/categories/", json=data, headers=self.get_user_headers(user_token)) as response:
            if response.status == 201:
                category = await response.json()
                logger.info(f"Создана новая категория: {name}")
                return category
            logger.error(f"Ошибка создания категории: {name}")
            return None

    async def delete_category(self, user_token: str, category_id: str) -> bool:
        """
        Удаляет категорию по её ID.

        Args:
            user_token (str): Токен пользователя.
            category_id (str): ID категории.

        Returns:
            bool: True, если удаление успешно, иначе False.
        """
        headers: Dict[str, str] = {"Authorization": f"Bearer {user_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/categories/{category_id}", headers=headers) as response:
                success = response.status == 204
                if success:
                    logger.info(f"Категория с ID {category_id} успешно удалена")
                else:
                    logger.error(f"Ошибка удаления категории с ID {category_id}")
                return success

    async def get_comments(self, user_token: str, task_id: str) -> List[Dict[str, Any]]:
        """
        Получает список комментариев к задаче.

        Args:
            user_token (str): Токен пользователя.
            task_id (str): ID задачи.

        Returns:
            List[Dict[str, Any]]: Список комментариев к задаче.
        """
        async with self.session.get(f"{self.fastapi_url}/tasks/{task_id}/comments", headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                comments = await response.json()
                logger.info(f"Получено {len(comments)} комментариев для задачи {task_id}")
                return comments
            logger.error(f"Ошибка получения комментариев для задачи {task_id}")
            return []

    async def create_comment(self, user_token: str, task_id: str, user_id: int, content: str) -> Optional[Dict[str, Any]]:
        """
        Создает новый комментарий к задаче.

        Args:
            user_token (str): Токен пользователя.
            task_id (str): ID задачи.
            user_id (int): ID пользователя.
            content (str): Содержание комментария.

        Returns:
            Optional[Dict[str, Any]]: Информация о созданном комментарии или None в случае ошибки.
        """
        data: Dict[str, Any] = {
            "content": content,
            "task_id": task_id,
            "user_id": user_id
        }
        async with self.session.post(f"{self.fastapi_url}/comments/", json=data, headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                comment = await response.json()
                logger.info(f"Создан новый комментарий для задачи {task_id}")
                return comment
            logger.error(f"Ошибка создания комментария для задачи {task_id}")
            return None

    async def delete_comment(self, user_token: str, comment_id: int) -> bool:
        """
        Удаляет комментарий по его ID.

        Args:
            user_token (str): Токен пользователя.
            comment_id (int): ID комментария.

        Returns:
            bool: True, если удаление успешно, иначе False.
        """
        async with self.session.delete(f"{self.fastapi_url}/comments/{comment_id}/",
                                       headers=self.get_user_headers(user_token)) as response:
            success = response.status == 200
            if success:
                logger.info(f"Комментарий с ID {comment_id} успешно удален")
            else:
                logger.error(f"Ошибка удаления комментария с ID {comment_id}")
            return success

    async def update_task_categories(self, user_token: str, task_id: str, category: List[str]) -> bool:
        """
        Обновляет категории задачи.

        Args:
            user_token (str): Токен пользователя.
            task_id (str): ID задачи.
            category (List[str]): Список новых категорий.

        Returns:
            bool: True, если обновление успешно, иначе False.
        """
        headers: Dict[str, str] = {"Authorization": f"Bearer {user_token}"}
        data: Dict[str, List[str]] = {"categories": category}
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.base_url}/tasks/{task_id}/", headers=headers,
                                   json=data) as response:
                success = response.status == 200
                if success:
                    logger.info(f"Категории задачи {task_id} успешно обновлены")
                else:
                    logger.error(f"Ошибка обновления категорий задачи {task_id}")
                return success

    async def update_task(self, user_token: str, task_id: str, **kwargs: Any) -> bool:
        """
        Обновляет информацию о задаче.

        Args:
            user_token (str): Токен пользователя.
            task_id (str): ID задачи.
            **kwargs: Параметры для обновления.

        Returns:
            bool: True, если обновление успешно, иначе False.
        """
        headers: Dict[str, str] = {"Authorization": f"Bearer {user_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.base_url}/tasks/{task_id}/", headers=headers, json=kwargs) as response:
                success = response.status == 200
                if success:
                    logger.info(f"Задача {task_id} успешно обновлена")
                else:
                    logger.error(f"Ошибка обновления задачи {task_id}")
                return success

    async def complete_and_delete_task(self, user_token: str, task_id: str) -> bool:
        """
        Завершает и удаляет задачу.

        Args:
            user_token (str): Токен пользователя.
            task_id (str): ID задачи.

        Returns:
            bool: True, если операция успешна, иначе False.
        """
        headers: Dict[str, str] = {"Authorization": f"Bearer {user_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/tasks/{task_id}/", headers=headers) as response:
                success = response.status == 204
                if success:
                    logger.info(f"Задача {task_id} успешно завершена и удалена")
                else:
                    logger.error(f"Ошибка завершения и удаления задачи {task_id}")
                return success

    def get_admin_headers(self) -> Dict[str, str]:
        """
        Возвращает заголовки для запросов от имени администратора.

        Returns:
            Dict[str, str]: Заголовки с токеном администратора.
        """
        return {"Authorization": f"Bearer {self.admin_token}"}

    def get_user_headers(self, user_token: str) -> Dict[str, str]:
        """
        Возвращает заголовки для запросов от имени пользователя.

        Args:
            user_token (str): Токен пользователя.

        Returns:
            Dict[str, str]: Заголовки с токеном пользователя.
        """
        return {"Authorization": f"Bearer {user_token}"}

api_service: APIService = APIService()