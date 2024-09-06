import time
import hashlib
from typing import Any, Dict
from django.db import models
from django.contrib.auth.models import User

class CustomPKModel(models.Model):
    id = models.CharField(max_length=64, primary_key=True, editable=False) # Уникальный идентификатор

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.id:
            timestamp: int = int(time.time() * 1000)
            hash_object = hashlib.sha256(str(timestamp).encode())
            self.id = hash_object.hexdigest()[:64]
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class Category(CustomPKModel):
    name = models.CharField(max_length=100) # Названия категории

    def __str__(self) -> str:
        return self.name

class Task(CustomPKModel):
    title = models.CharField(max_length=200) # Заголовок задачи
    description = models.TextField(blank=True) # Описание задачи
    created_at = models.DateTimeField(auto_now_add=True) # Дата и время создания задачи
    due_date = models.DateTimeField(null=True, blank=True) # Срок выполнения задачи
    completed = models.BooleanField(default=False) # Статус выполнения задачи
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks') # Связь с пользователем (ForeignKey). При удалении пользователя удаляются все его задачи.
    categories = models.ManyToManyField(Category, related_name='tasks') # Связь многие-ко-многим с категориями. Одна задача может иметь несколько категорий, и одна категория может быть у нескольких задач.

    def __str__(self) -> str:
        return self.title