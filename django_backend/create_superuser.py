import os
import django
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')
django.setup()

# Создаем суперпользователя
if not User.objects.filter(username=os.getenv("API_USERNAME_TODO")).exists():
    User.objects.create_superuser(os.getenv("API_USERNAME_TODO"), 'admin@example.com', os.getenv("API_PASSWORD_TODO"))