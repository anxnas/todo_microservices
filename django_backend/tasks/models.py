import time
import hashlib
from typing import Any, Dict
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from profi_log import MasterLogger

# Инициализация логгера
# Получаем уровень логирования из настроек Django
log_level = getattr(settings, 'PROFI_LOG_LEVEL', 'INFO')

# Получаем настройку для цветного логирования
use_colored_console = getattr(settings, 'PROFI_LOG_COLORED_CONSOLE', True)

# Инициализация логгера
logger = MasterLogger("logs/models.log", level=log_level)

# Настройка цветного логирования в консоль, если это включено в настройках
if use_colored_console:
    logger.setup_colored_console_logging()


class CustomPKModel(models.Model):
    """
    Абстрактная модель с кастомным первичным ключом.

    Генерирует уникальный идентификатор на основе текущего времени.
    """
    id = models.CharField(max_length=64, primary_key=True, editable=False) # Уникальный идентификатор

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохраняет модель, генерируя уникальный ID, если он еще не установлен.
        """
        if not self.id:
            timestamp: int = int(time.time() * 1000)
            hash_object = hashlib.sha256(str(timestamp).encode())
            self.id = hash_object.hexdigest()[:64]
            logger.info(f"Сгенерирован новый ID для {self.__class__.__name__}: {self.id}")
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка при сохранении {self.__class__.__name__}: {str(e)}")

    class Meta:
        abstract = True

class Category(CustomPKModel):
    """Модель для категорий задач."""
    name = models.CharField(max_length=100) # Названия категории

    def __str__(self) -> str:
        return self.name

class Task(CustomPKModel):
    """Модель для задач."""
    title = models.CharField(max_length=200) # Заголовок задачи
    description = models.TextField(blank=True) # Описание задачи
    created_at = models.DateTimeField(auto_now_add=True) # Дата и время создания задачи
    due_date = models.DateTimeField(null=True, blank=True) # Срок выполнения задачи
    completed = models.BooleanField(default=False) # Статус выполнения задачи
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks') # Связь с пользователем (ForeignKey). При удалении пользователя удаляются все его задачи.
    categories = models.ManyToManyField(Category, related_name='tasks') # Связь многие-ко-многим с категориями. Одна задача может иметь несколько категорий, и одна категория может быть у нескольких задач.

    def __str__(self) -> str:
        return self.title