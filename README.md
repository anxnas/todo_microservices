django_backend/
├── todo_list/
│   ├── __init__.py+
│   ├── settings.py+
│   ├── urls.py+
│   ├── wsgi.py+
├── tasks/
│   ├── __init__.py+
│   ├── models.py+
│   ├── views.py+
│   ├── serializers.py+
│   ├── admin.py+
│   ├── tests.py+
├── manage.py+
├── create_db.py+
├── Dockerfile+
├── requirements.txt+
Структура+
Типизация+
Контейнер+
Тестирование+
Отчёт об уязвимостях+
Документация+
Исключения+
Логирование+
ООП+
fastapi_microservice/
├── app/
│   ├── __init__.py+
│   ├── main.py+
│   ├── models.py+
│   ├── schemas.py+
│   ├── crud.py+
│   ├── database.py+
│   ├── config.py+
├── Dockerfile+
├── requirements.txt+
Структура+
Типизация-
Контейнер+
Тестирование+
Отчёт об уязвимостях+
Документация+
Исключения+
Логирование+
ООП+
telegram_bot/
├── bot/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── tasks.py
│   │   ├── comments.py
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── reply.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── django_api.py
│   │   ├── fastapi_api.py
│   ├── locales/
│   │   ├── en/
│   │   │   ├── LC_MESSAGES/
│   │   │       ├── bot.po
│   │   ├── ru/
│   │   │   ├── LC_MESSAGES/
│   │   │       ├── bot.po
├── Dockerfile
├── requirements.txt