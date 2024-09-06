from django.contrib import admin
from typing import Tuple
from .models import Task, Category

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display: Tuple[str, ...] = ('title', 'user', 'created_at', 'completed')
    list_filter: Tuple[str, ...] = ('completed', 'created_at')
    search_fields: Tuple[str, ...] = ('title', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display: Tuple[str, ...] = ('name',)