import json
import asyncpg
from config import config
from typing import Dict, Any, Optional

class Localization:
    def __init__(self):
        self.locales: Dict[str, Dict[str, str]] = {}
        self.load_locales()

    def load_locales(self) -> None:
        with open('locales/ru.json', 'r', encoding='utf-8') as f:
            self.locales['ru'] = json.load(f)
        with open('locales/en.json', 'r', encoding='utf-8') as f:
            self.locales['en'] = json.load(f)

    def get_text(self, key: str, locale: str = 'ru') -> str:
        try:
            return self.locales.get(locale, {}).get(key, key)
        except Exception as e:
            print(f"Error getting localized text for key '{key}' and locale '{locale}': {e}")
            return key

    async def init_db(self) -> None:
        # Подключение к серверу PostgreSQL
        system_conn: asyncpg.Connection = await asyncpg.connect(
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT
        )

        # Проверка существования базы данных
        db_exists: Optional[int] = await system_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            config.POSTGRES_DB_TODO
        )

        if not db_exists:
            # Создание базы данных
            await system_conn.execute(f"CREATE DATABASE {config.POSTGRES_DB_TODO}")

        await system_conn.close()

        # Подключение к созданной базе данных
        conn: asyncpg.Connection = await asyncpg.connect(
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            database=config.POSTGRES_DB_TODO,
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT
        )

        # Создание таблицы telegram_user, если она не существует
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS telegram_user (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                locale VARCHAR(10) NOT NULL DEFAULT 'ru'
            )
        """)

        await conn.close()

    async def set_user_locale(self, telegram_id: int, locale: str) -> None:
        await self.init_db()  # Убедимся, что база данных и таблица существуют
        conn: asyncpg.Connection = await asyncpg.connect(
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            database=config.POSTGRES_DB_TODO,
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT
        )
        await conn.execute(
            "INSERT INTO telegram_user (telegram_id, locale) VALUES ($1, $2) "
            "ON CONFLICT (telegram_id) DO UPDATE SET locale = $2",
            telegram_id, locale
        )
        await conn.close()

    async def get_user_locale(self, telegram_id: int) -> str:
        await self.init_db()  # Убедимся, что база данных и таблица существуют
        conn: asyncpg.Connection = await asyncpg.connect(
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            database=config.POSTGRES_DB_TODO,
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT
        )
        locale: Optional[str] = await conn.fetchval(
            "SELECT locale FROM telegram_user WHERE telegram_id = $1",
            telegram_id
        )
        await conn.close()
        return locale or 'ru'

localization: Localization = Localization()