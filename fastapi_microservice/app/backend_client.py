import httpx
from .config import settings

async def get_token() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.DJANGO_BACKEND_URL}/api/token/",
            data={"username": settings.API_USERNAME_TODO, "password": settings.API_PASSWORD_TODO}
        )
        if response.status_code == 200:
            return response.json()["access"]
        else:
            print(f"Failed to get token. Status: {response.status_code}, Response: {response.text}")

async def check_task_exists(task_id: str) -> bool:
    token = await get_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.DJANGO_BACKEND_URL}/api/tasks/{task_id}/",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.status_code == 200

async def get_task_details(task_id: str) -> dict:
    token = await get_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.DJANGO_BACKEND_URL}/api/tasks/{task_id}/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None