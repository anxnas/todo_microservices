import psycopg2
from django.conf import settings


def create_database() -> None:
    conn = psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )
    conn.autocommit = True
    cursor = conn.cursor()

    db_name: str = settings.DATABASES['default']['NAME']

    try:
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"База данных {db_name} успешно создана.")
    except psycopg2.errors.DuplicateDatabase:
        pass
    finally:
        cursor.close()
        conn.close()