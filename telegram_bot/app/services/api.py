import aiohttp
from typing import List
from config import config
from models.user import User

class APIService:
    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.fastapi_url = config.FASTAPI_BASE_URL
        self.session = None
        self.admin_token = None

    async def create_session(self):
        self.session = aiohttp.ClientSession()
        # Авторизация суперпользователя при создании сессии
        await self.admin_login(config.API_USERNAME_TODO, config.API_PASSWORD_TODO)

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def admin_login(self, username: str, password: str):
        async with self.session.post(f"{self.base_url}/token/", data={"username": username, "password": password}) as response:
            if response.status == 200:
                data = await response.json()
                self.admin_token = data["access"]
                return data["user_id"]
            return None

    async def user_login(self, username: str, password: str):
        async with self.session.post(f"{self.base_url}/token/", data={"username": username, "password": password}) as response:
            if response.status == 200:
                data = await response.json()
                return data["access"], data["user_id"]
            return None, None

    async def get_user_info(self, telegram_id: int):
        async with self.session.get(f"{self.base_url}/users/{telegram_id}/public_info/", headers=self.get_admin_headers()) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def create_user(self, telegram_id: int, username: str, password: str):
        data = {
            "username": username,
            "password": password,
            "telegram_id": telegram_id
        }
        async with self.session.post(f"{self.base_url}/users/", json=data, headers=self.get_admin_headers()) as response:
            if response.status == 201:
                return await response.json()
            return None

    async def get_task(self, user_token: str, task_id: int):
        async with self.session.get(f"{self.base_url}/tasks/{task_id}/",
                                    headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def get_tasks(self, user_token: str):
        async with self.session.get(f"{self.base_url}/tasks/", headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                return await response.json()
            return []

    async def create_task(self, user_token: str, title: str, description: str, due_date: str, categories: list):
        data = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "categories": [{"name": cat} for cat in categories]
        }
        async with self.session.post(f"{self.base_url}/tasks/", json=data, headers=self.get_user_headers(user_token)) as response:
            if response.status == 201:
                return await response.json()
            return None

    async def get_categories(self, user_token: str):
        async with self.session.get(f"{self.base_url}/categories/", headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                return await response.json()
            return []

    async def create_category(self, user_token: str, name: str):
        data = {"name": name}
        async with self.session.post(f"{self.base_url}/categories/", json=data, headers=self.get_user_headers(user_token)) as response:
            if response.status == 201:
                return await response.json()
            return None

    async def delete_category(self, user_token: str, category_id: str) -> bool:
        headers = {"Authorization": f"Bearer {user_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/categories/{category_id}", headers=headers) as response:
                if response.status == 204:
                    return True
                else:
                    return False

    async def get_comments(self, user_token: str, task_id: int):
        async with self.session.get(f"{self.fastapi_url}/tasks/{task_id}/comments", headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                return await response.json()
            return []

    async def create_comment(self, user_token: str, task_id: int, user_id: int, content: str):
        data = {
            "content": content,
            "task_id": task_id,
            "user_id": user_id
        }
        async with self.session.post(f"{self.fastapi_url}/comments/", json=data, headers=self.get_user_headers(user_token)) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def delete_comment(self, user_token: str, comment_id: int):
        async with self.session.delete(f"{self.fastapi_url}/comments/{comment_id}/",
                                       headers=self.get_user_headers(user_token)) as response:
            return response.status == 200

    async def update_task_categories(self, user_token: str, task_id: str, category: List[str]) -> bool:
        headers = {"Authorization": f"Bearer {user_token}"}
        data = {"categories": category}
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.base_url}/tasks/{task_id}/", headers=headers,
                                   json=data) as response:
                if response.status == 200:
                    return True
                else:
                    return False

    async def update_task(self, user_token: str, task_id: str, **kwargs) -> bool:
        headers = {"Authorization": f"Bearer {user_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{self.base_url}/tasks/{task_id}/", headers=headers, json=kwargs) as response:
                if response.status == 200:
                    return True
                else:
                    return False

    async def complete_and_delete_task(self, user_token: str, task_id: str) -> bool:
        headers = {"Authorization": f"Bearer {user_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/tasks/{task_id}/", headers=headers) as response:
                if response.status == 204:
                    return True
                else:
                    return False

    def get_admin_headers(self):
        return {"Authorization": f"Bearer {self.admin_token}"}

    def get_user_headers(self, user_token: str):
        return {"Authorization": f"Bearer {user_token}"}

api_service = APIService()