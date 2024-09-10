import os
from typing import Optional

class Config:
    """
    Класс конфигурации для хранения настроек приложения.

    Attributes:
        BOT_TOKEN (Optional[str]): Токен Telegram бота. Получается из переменной окружения "BOT_TOKEN".
        API_BASE_URL (str): Базовый URL API. Получается из переменной окружения "DJANGO_URL".
        FASTAPI_BASE_URL (str): Базовый URL FastAPI. Получается из переменной окружения "FASTAPI_URL".
        API_USERNAME_TODO (Optional[str]): Имя пользователя для API TODO. Получается из переменной окружения "API_USERNAME_TODO".
        API_PASSWORD_TODO (Optional[str]): Пароль для API TODO. Получается из переменной окружения "API_PASSWORD_TODO".
        POSTGRES_USER (Optional[str]): Имя пользователя PostgreSQL. Получается из переменной окружения "POSTGRES_USER".
        POSTGRES_PASSWORD (Optional[str]): Пароль PostgreSQL. Получается из переменной окружения "POSTGRES_PASSWORD".
        POSTGRES_DB_TODO (Optional[str]): Имя базы данных PostgreSQL для TODO. Получается из переменной окружения "POSTGRES_DB_TODO".
        POSTGRES_HOST (Optional[str]): Хост PostgreSQL. Получается из переменной окружения "POSTGRES_HOST".
        POSTGRES_PORT (Optional[str]): Порт PostgreSQL. Получается из переменной окружения "POSTGRES_PORT".
    """
    BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
    API_BASE_URL: str = f'{os.getenv("DJANGO_URL")}/api'
    FASTAPI_BASE_URL: str = os.getenv("FASTAPI_URL")
    API_USERNAME_TODO: Optional[str] = os.getenv("API_USERNAME_TODO")
    API_PASSWORD_TODO: Optional[str] = os.getenv("API_PASSWORD_TODO")
    POSTGRES_USER: Optional[str] = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB_TODO: Optional[str] = os.getenv("POSTGRES_DB_TODO")
    POSTGRES_HOST: Optional[str] = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: Optional[str] = os.getenv("POSTGRES_PORT")

config = Config()