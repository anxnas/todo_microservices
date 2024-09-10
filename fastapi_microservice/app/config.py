import os
from urllib.parse import quote_plus
from profi_log import MasterLogger

class Settings:
    PROJECT_NAME: str = "FastAPI Microservice - TODO Project"
    PROJECT_VERSION: str = "1.0.0"
    POSTGRES_USER: str = quote_plus(os.getenv("POSTGRES_USER", "todo_user"))
    POSTGRES_PASSWORD = quote_plus(os.getenv("POSTGRES_PASSWORD", "todo_password"))
    POSTGRES_SERVER: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB_TODO", "todo_db")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    DJANGO_BACKEND_URL: str = os.getenv("DJANGO_URL", "http://localhost:8000")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8080"))
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    API_USERNAME_TODO: str = os.getenv("API_USERNAME_TODO", "admin")
    API_PASSWORD_TODO: str = os.getenv("API_PASSWORD_TODO", "12345678")
    LOGGER = MasterLogger("logs/register.log", level='INFO')
    LOGGER_CONSOLE = LOGGER.setup_colored_console_logging()

settings = Settings()