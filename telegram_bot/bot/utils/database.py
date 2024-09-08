import asyncpg
from asyncpg.exceptions import UndefinedTableError
from config import DATABASE_URL
from typing import Optional

async def get_connection():
    return await asyncpg.connect(DATABASE_URL)

async def init_db():
    conn = await get_connection()
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS telegram_user (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                locale VARCHAR(10) NOT NULL DEFAULT 'en'
            )
        ''')
    finally:
        await conn.close()

async def get_user_locale(telegram_id: int) -> str:
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            'SELECT locale FROM telegram_user WHERE telegram_id = $1',
            telegram_id
        )
        return row['locale'] if row else 'en'
    except UndefinedTableError:
        await init_db()
    finally:
        await conn.close()

async def set_user_locale(telegram_id: int, locale: str):
    conn = await get_connection()
    try:
        await conn.execute('''
            INSERT INTO telegram_user (telegram_id, locale)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) 
            DO UPDATE SET locale = $2
        ''', telegram_id, locale)
        print(f"Set locale {locale} for user {telegram_id}")  # Отладочный вывод
    finally:
        await conn.close()

async def get_or_create_user(telegram_id: int) -> tuple[int, str]:
    conn = await get_connection()
    try:
        row = await conn.fetchrow('''
            INSERT INTO telegram_user (telegram_id)
            VALUES ($1)
            ON CONFLICT (telegram_id) DO UPDATE SET telegram_id = $1
            RETURNING id, locale
        ''', telegram_id)
        return row['id'], row['locale']
    except UndefinedTableError:
        await init_db()
    finally:
        await conn.close()