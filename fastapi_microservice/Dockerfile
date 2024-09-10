# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт
EXPOSE 8080

# Запускаем сервер
CMD ["python", "run"]