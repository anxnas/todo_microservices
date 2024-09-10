# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app/telegram_bot

# Копируем файлы проекта
COPY app /app/telegram_bot

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && pip install --no-cache-dir -r requirements.txt

# Устанавливаем переменные окружения
ENV API_USERNAME_TODO=ВАШ_ЛОГИН_СУПЕРПОЛЬЗОВАТЕЛЯ
ENV API_PASSWORD_TODO=ВАШ_ПАРОЛЬ_СУПЕРПОЛЬЗОВАТЕЛЯ
ENV BOT_TOKEN=ТОКЕН_БОТА
ENV POSTGRES_DB_TODO=todo_db
ENV POSTGRES_HOST=localhost
ENV POSTGRES_USER=ЛОГИН_БД
ENV POSTGRES_PASSWORD=ПАРОЛЬ_БД
ENV POSTGRES_PORT=5432
ENV PYTHONUNBUFFERED=1

# Запускаем бота
CMD ["python", "bot.py"]