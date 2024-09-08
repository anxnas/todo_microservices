import aiohttp
from config import DJANGO_API_URL, FASTAPI_API_URL

async def get_comments(token: str, task_id: int):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get(f"{FASTAPI_API_URL}/tasks/{task_id}/comments", headers=headers) as response:
            if response.status == 200:
                comments = await response.json()
                for comment in comments:
                    user_id = comment.get('user_id')
                    if user_id:
                        async with session.get(f"{DJANGO_API_URL}/api/users/{user_id}/public_info/", headers=headers) as user_response:
                            if user_response.status == 200:
                                user_info = await user_response.json()
                                comment['username'] = user_info.get('username', 'Unknown user')
                            else:
                                comment['username'] = 'Unknown user'
                    else:
                        comment['username'] = 'Unknown user'
                return comments
            return []

async def create_comment(token: str, task_id: int, content: str, user_id: int):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "content": content,
            "task_id": task_id,
            "user_id": user_id
        }
        async with session.post(f"{FASTAPI_API_URL}/comments/", headers=headers, json=data) as response:
            if response.status == 200:
                return await response.json()
            return None

async def update_comment(token: str, comment_id: int, content: str, task_id: int, user_id: int):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "content": content,
            "task_id": task_id,
            "user_id": user_id
        }
        async with session.put(f"{FASTAPI_API_URL}/comments/{comment_id}", headers=headers, json=data) as response:
            if response.status == 200:
                return await response.json()
            return None

async def delete_comment(token: str, comment_id: int):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        async with session.delete(f"{FASTAPI_API_URL}/comments/{comment_id}", headers=headers) as response:
            return response.status == 200