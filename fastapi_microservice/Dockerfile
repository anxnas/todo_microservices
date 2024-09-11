# Используем официальный образ Python
FROM python:3.9-buster

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

RUN apt-get update && \
    apt-get install -y gcc libpq-dev&& \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт
EXPOSE 8080