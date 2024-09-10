import aiohttp
from typing import List, Dict, Any, Optional, Tuple
from config import config
from models.user import User

class APIService:
    def __init__(self):
        self.base_url: str = config.API_BASE_URL
        self.fastapi_url: str = config.FASTAPI_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self.admin_token: Optional[str] = None

    async def create_session(self) -> None:
        self.session = aiohttp.ClientSession()
        await self.admin_login(config.API_USERNAME_TODO, config.API_PASSWORD_TODO)

    async def close_session(self) -> None:
        if self.session:
            await self.session.close()

    async def admin_login(self, username: str, password: str) -> Optional[int]:
        async with self.session.post(f"{self.base_url}/token/", data={"username": username, "password": password}) as response:
            if response.status == 200:
                data: Dict[str, Any] = await response.json()
                self.admin_token = data["access"]
                return data["user_id"]
            return None

    async def user_login(self, username: str, password: str) -> Tuple[Optional[str], Optional[int]]:
        async with self.session.post(f"{self.base_url}/token/", data={"username": username, "password": password}) as response:
            if response.status == 200:
                data: Dict[str, Any] = await response.json()
                return data["access"], data["user_id"]
            return None, None

    async def get_user_info(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        async with self.session.get(f"{self.base_url}/users/{telegram_id}/public_info/", headers=self.get_admin_headers()) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def create_user(self, telegram_id: int, username: str, password: str) -> Optional[Dict[str, Any]]:
        data: Dict[str, Any] = {
            "username": username,
            "password": password,
            "telegram_id": telegram_id
        }
        async with self.session.post(f"{self.base_url}/users/", json=data, headers=self.get_admin_headers()) as response:
            if response.status == 201:
                return await response.json()
            return None

    async def get_task(self, user_token: str, task_id: int) -> Optional[Dict[str, Any]]:
        async with self.session.get(f"{self.base_url}/tasks/{task_id}/",
                                    headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def get_tasks(self, user_token: str) -> List[Dict[str, Any]]:
        async with self.session.get(f"{self.base_url}/tasks/", headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                return await response.json()
            return []

    async def create_task(self, user_token: str, title: str, description: str, due_date: str, categories: List[str]) -> Optional[Dict[str, Any]]:
        data: Dict[str, Any] = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "categories": [{"name": cat} for cat in categories]
        }
        async with self.session.post(f"{self.base_url}/tasks/", json=data, headers=self.get_user_headers(user_token)) as response:
            if response.status == 201:
                return await response.json()
            return None

    async def get_categories(self, user_token: str) -> List[Dict[str, Any]]:
        async with self.session.get(f"{self.base_url}/categories/", headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                return await response.json()
            return []

    async def create_category(self, user_token: str, name: str) -> Optional[Dict[str, Any]]:
        data: Dict[str, str] = {"name": name}
        async with self.session.post(f"{self.base_url}/categories/", json=data, headers=self.get_user_headers(user_token)) as response:
            if response.status == 201:
                return await response.json()
            return None

    async def delete_category(self, user_token: str, category_id: str) -> bool:
        headers: Dict[str, str] = {"Authorization": f"Bearer {user_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/categories/{category_id}", headers=headers) as response:
                return response.status == 204

    async def get_comments(self, user_token: str, task_id: int) -> List[Dict[str, Any]]:
        async with self.session.get(f"{self.fastapi_url}/tasks/{task_id}/comments", headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                return await response.json()
            return []

    async def create_comment(self, user_token: str, task_id: int, user_id: int, content: str) -> Optional[Dict[str, Any]]:
        data: Dict[str, Any] = {
            "content": content,
            "task_id": task_id,
            "user_id": user_id
        }
        async with self.session.post(f"{self.fastapi_url}/comments/", json=data, headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def delete_comment(self, user_token: str, comment_id: int) -> bool:
        async with self.session.delete(f"{self.fastapi_url}/comments/{comment_id}/",
                                       headers=self.get_user_headers(user_token)) as response:
            return response.status == 200

    async def update_task_categories(self, user_token: str, task_id: str, category: List[str]) -> bool:
        headers: Dict[str, str] = {"Authorization": f"Bearer {user_token}"}
        data: Dict[str, List[str]] = {"categories": category}
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.base_url}/tasks/{task_id}/", headers=headers,
                                   json=data) as response:
                return response.status == 200

    async def update_task(self, user_token: str, task_id: str, **kwargs: Any) -> bool:
        headers: Dict[str, str] = {"Authorization": f"Bearer {user_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.base_url}/tasks/{task_id}/", headers=headers, json=kwargs) as response:
                return response.status == 200

    async def complete_and_delete_task(self, user_token: str, task_id: str) -> bool:
        headers: Dict[str, str] = {"Authorization": f"Bearer {user_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/tasks/{task_id}/", headers=headers) as response:
                return response.status == 204

    def get_admin_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.admin_token}"}

    def get_user_headers(self, user_token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {user_token}"}

api_service: APIService = APIService()