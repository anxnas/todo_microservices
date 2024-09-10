import os

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    API_BASE_URL = "http://127.0.0.1:8000/api"
    FASTAPI_BASE_URL = "http://127.0.0.1:8080"
    API_USERNAME_TODO = os.getenv("API_USERNAME_TODO")
    API_PASSWORD_TODO = os.getenv("API_PASSWORD_TODO")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB_TODO = os.getenv("POSTGRES_DB_TODO")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")

config = Config()