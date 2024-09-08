import os
from urllib.parse import quote_plus

BOT_TOKEN = '6057778865:AAHtlPGgVzQKB5Bny62WrxCNS90YPKGAcMM'
DJANGO_API_URL = "http://127.0.0.1:8000"
FASTAPI_API_URL = 'http://127.0.0.1:8080'
API_USERNAME = os.getenv('API_USERNAME_TODO')
API_PASSWORD = os.getenv('API_PASSWORD_TODO')
POSTGRES_USER: str = quote_plus(os.getenv("POSTGRES_USER", "todo_user"))
POSTGRES_PASSWORD = quote_plus(os.getenv("POSTGRES_PASSWORD", "todo_password"))
POSTGRES_SERVER: str = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB: str = os.getenv("POSTGRES_DB_TODO", "todo_db")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"