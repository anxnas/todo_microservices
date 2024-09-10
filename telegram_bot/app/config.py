import os
from typing import Optional

class Config:
    BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
    API_BASE_URL: str = "http://127.0.0.1:8000/api"
    FASTAPI_BASE_URL: str = "http://127.0.0.1:8080"
    API_USERNAME_TODO: Optional[str] = os.getenv("API_USERNAME_TODO")
    API_PASSWORD_TODO: Optional[str] = os.getenv("API_PASSWORD_TODO")
    POSTGRES_USER: Optional[str] = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB_TODO: Optional[str] = os.getenv("POSTGRES_DB_TODO")
    POSTGRES_HOST: Optional[str] = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: Optional[str] = os.getenv("POSTGRES_PORT")

config = Config()