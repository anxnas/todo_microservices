import os
import django
from django.contrib.auth import get_user_model
from django.conf import settings

logger = settings.LOGGER.get_logger('create_superuser')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')
django.setup()

User = get_user_model()

# Проверьте, существует ли суперпользователь
if not User.objects.filter(username=os.environ.get('DJANGO_SUPERUSER_USERNAME')).exists():
    User.objects.create_superuser(
        username=os.environ.get('DJANGO_SUPERUSER_USERNAME'),
        email=os.environ.get('DJANGO_SUPERUSER_EMAIL'),
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    )
    logger.info("Суперпользователь создан")
else:
    logger.info("Суперпользователь уже существует")