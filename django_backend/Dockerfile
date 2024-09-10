# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app/django_backend

# Копируем файлы проекта
COPY . /app/django_backend

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && pip install --no-cache-dir -r requirements.txt

# Устанавливаем переменные окружения
ENV DJANGO_SETTINGS_MODULE=todo_list.settings
ENV PYTHONUNBUFFERED=1
ENV API_USERNAME_TODO=ВАШ_ЛОГИН_СУПЕРПОЛЬЗОВАТЕЛЯ
ENV API_PASSWORD_TODO=ВАШ_ПАРОЛЬ_СУПЕРПОЛЬЗОВАТЕЛЯ
ENV POSTGRES_DB_TODO=todo_db
ENV POSTGRES_HOST=localhost
ENV POSTGRES_USER=ЛОГИН_БД
ENV POSTGRES_PASSWORD=ПАРОЛЬ_БД
ENV POSTGRES_PORT=5432

# Открываем порт
EXPOSE 8000

# Запускаем сервер
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]