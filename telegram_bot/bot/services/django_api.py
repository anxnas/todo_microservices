import aiohttp
from config import DJANGO_API_URL, API_USERNAME, API_PASSWORD

async def get_admin_token():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{DJANGO_API_URL}/api/token/", json={
            "username": API_USERNAME,
            "password": API_PASSWORD
        }) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("access")
    return None

async def get_token(username: str, password: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{DJANGO_API_URL}/api/token/", json={
            "username": username,
            "password": password
        }) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("access")
    return None

async def get_tasks(token: str):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get(f"{DJANGO_API_URL}/api/tasks/", headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return []

async def create_task(token: str, title: str, description: str, due_date: str, categories: list):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "categories": [{"name": cat} for cat in categories]
        }
        async with session.post(f"{DJANGO_API_URL}/api/tasks/", headers=headers, json=data) as response:
            if response.status == 201:
                return await response.json()
            return None

async def get_task_details(token: str, task_id: str):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get(f"{DJANGO_API_URL}/api/tasks/{task_id}/", headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return None

async def update_task(token: str, task_id: str, data: dict):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        async with session.put(f"{DJANGO_API_URL}/api/tasks/{task_id}/", headers=headers, json=data) as response:
            if response.status == 200:
                return await response.json()
            return None

async def check_user(user_id: int):
    admin_token = await get_admin_token()
    if not admin_token:
        raise Exception("Failed to get admin token")

    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {admin_token}"}
        async with session.get(f"{DJANGO_API_URL}/api/users/{user_id}/public_info", headers=headers) as response:
            return response.status == 200

async def create_user(user_id: int, username: str, password: str):
    admin_token = await get_admin_token()
    if not admin_token:
        raise Exception("Failed to get admin token")

    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {admin_token}"}
        async with session.post(f"{DJANGO_API_URL}/api/users/", headers=headers, json={
            "id": user_id,
            "username": username,
            "password": password
        }) as response:
            if response.status == 201:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"Failed to create user. Status: {response.status}, Error: {error_text}")