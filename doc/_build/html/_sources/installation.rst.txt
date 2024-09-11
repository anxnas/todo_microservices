Установка и запуск
==================

Предварительные требования
--------------------------

- Docker
- Docker Compose

Шаги установки
--------------

1. Клонируйте репозиторий:

   .. code-block:: bash

      git clone https://github.com/your-repo/project.git
      cd project

2. Проверьте переменные:

    Отредактируйте `docker-compose.yml`. Обязательно замените значения в переменных окружений на нужные.

2. Запустите Docker Compose:

   .. code-block:: bash

      docker-compose up --build

3. Проект будет доступен по следующим адресам:
   - Django Backend: `http://localhost:8000`
   - FastAPI Microservice: `http://localhost:8080`
   - Telegram Bot: через Telegram