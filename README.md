# Система управления задачами

![Логотип проекта](.github/logo.png)

Этот проект представляет собой комплексное решение для управления задачами, включающее Django Backend, FastAPI Microservice и Telegram Bot. Все компоненты интегрированы с использованием Docker для упрощения развертывания и управления.

## Оглавление

- [Компоненты проекта](#компоненты-проекта)
- [Предварительные требования](#предварительные-требования)
- [Установка и запуск](#установка-и-запуск)
- [Структура проекта](#структура-проекта)
- [Использование](#использование)
- [Разработка](#разработка)
- [Документация](#документация)
- [API Reference](#api-reference)
- [Вклад в проект](#вклад-в-проект)
- [Лицензия](#лицензия)
- [Контакты](#контакты)

## Компоненты проекта

1. **Django Backend**: 
   - Основной бэкенд для управления задачами
   - RESTful API для создания, чтения, обновления и удаления задач
   - Аутентификация и авторизация пользователей
   - Интеграция с базой данных PostgreSQL

2. **FastAPI Microservice**: 
   - Микросервис для работы с комментариями
   - Высокопроизводительный API на основе FastAPI
   - Асинхронная обработка запросов
   - Интеграция с Redis для кэширования

3. **Telegram Bot**: 
   - Интерфейс для взаимодействия с пользователями через Telegram
   - Поддержка команд для управления задачами
   - Многоязычный интерфейс
   - Интеграция с Django Backend и FastAPI Microservice
  
## Предварительные требования

- Docker
- Docker Compose
- Git
- Python 3.9+ (для локальной разработки)

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/anxnas/todo_microservices.git
   cd project
   ```

2. Отредактируйте `docker-compose.yml`. Обязательно замените значения в переменных окружений на нужные.

3. Запустите Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. После успешного запуска, проект будет доступен по следующим адресам:
   - Django Backend: `http://localhost:8000 (пример)`
   - FastAPI Microservice: `http://localhost:8080 (пример)`
   - Telegram Bot: через Telegram (найдите бота по имени @YourBotName)

## Использование

### Django Backend

1. Доступ к админ-панели:
   - Перейдите по адресу `http://localhost:8000/admin/`
   - Войдите, используя учетные данные суперпользователя

2. API endpoints:
   - Список задач: GET `http://localhost:8000/api/tasks/`
   - Создание задачи: POST `http://localhost:8000/api/tasks/`
   - Детали задачи: GET `http://localhost:8000/api/tasks/{id}/`
   - Обновление задачи: PUT `http://localhost:8000/api/tasks/{id}/`
   - Удаление задачи: DELETE `http://localhost:8000/api/tasks/{id}/`

### FastAPI Microservice

1. API endpoints:
   - Список комментариев: GET `http://localhost:8080/tasks/{task_id}/comments`
   - Создание комментария: POST `http://localhost:8080/comments/`
   - Обновление комментария: PUT `http://localhost:8080/comments/{id}/`
   - Удаление комментария: DELETE `http://localhost:8080/comments/{id}/`

### Telegram Bot

1. Найдите бота в Telegram по имени @YourBotName
2. Начните взаимодействие, отправив команду `/start`

## Разработка

Для локальной разработки отдельных компонентов:

1. Django Backend:
   ```bash
   cd django_backend
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py makemigration
   python manage.py migrate
   python manage.py runserver
   ```

2. FastAPI Microservice:
   ```bash
   cd fastapi_microservice
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python run.py
   ```

3. Telegram Bot:
   ```bash
   cd telegram_bot
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cd app
   python bot.py
   ```

## Документация

Полная документация проекта доступна по [ссылке](https://anxnas.github.io/todo_microservices/index.html)

## Лицензия

Этот проект лицензирован под GPL-3.0 license - см. файл [LICENSE](LICENSE) для деталей.

## Контакты

Хренов Святослав (anxnas) - Канал в тг: [@anxnas](https://t.me/anxnas)
