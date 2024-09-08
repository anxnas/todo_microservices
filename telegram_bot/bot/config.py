import os
from pathlib import Path

BOT_TOKEN = os.getenv("BOT_TOKEN")
DJANGO_API_URL = "http://127.0.0.1:8000"
FASTAPI_API_URL = 'http://127.0.0.1:8080'

BASE_DIR = Path(__file__).resolve().parent
LOCALES_DIR = BASE_DIR / 'locales'