from django.contrib import admin
from typing import Tuple, Any
from django.http import HttpRequest
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from .models import Task, Category
from django.conf import settings

logger = settings.LOGGER.get_logger('admin')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Task.
    """
    list_display: Tuple[str, ...] = ('title', 'user', 'created_at', 'completed')
    list_filter: Tuple[str, ...] = ('completed', 'created_at')
    search_fields: Tuple[str, ...] = ('title', 'description')

    def save_model(self, request: HttpRequest, obj: Task, form: Any, change: bool) -> None:
        """
        Сохраняет модель Task и логирует действие.

        Args:
            request (HttpRequest): Объект запроса.
            obj (Task): Объект задачи.
            form (Any): Форма модели.
            change (bool): Флаг, указывающий на изменение существующей модели.

        Raises:
            ValidationError: Если возникла ошибка при сохранении модели.
        """
        try:
            action = "изменена" if change else "создана"
            super().save_model(request, obj, form, change)
            logger.info(f"Задача '{obj.title}' {action} пользователем {request.user}")
        except Exception as e:
            logger.log_exception(f"Ошибка при сохранении задачи '{obj.title}': {str(e)}")
            raise ValidationError(f"Не удалось сохранить задачу: {str(e)}")

    def delete_model(self, request: HttpRequest, obj: Task) -> None:
        """
        Удаляет модель Task и логирует действие.

        Args:
            request (HttpRequest): Объект запроса.
            obj (Task): Объект задачи.

        Raises:
            ValidationError: Если возникла ошибка при удалении модели.
        """
        try:
            title = obj.title
            super().delete_model(request, obj)
            logger.info(f"Задача '{title}' удалена пользователем {request.user}")
        except Exception as e:
            logger.log_exception(f"Ошибка при удалении задачи '{obj.title}': {str(e)}")
            raise ValidationError(f"Не удалось удалить задачу: {str(e)}")

    def get_search_results(self, request: HttpRequest, queryset: QuerySet, search_term: str) -> Tuple[QuerySet, bool]:
        """
        Выполняет поиск по задачам и логирует действие.

        Args:
            request (HttpRequest): Объект запроса.
            queryset (QuerySet): Исходный QuerySet.
            search_term (str): Поисковый запрос.

        Returns:
            Tuple[QuerySet, bool]: Кортеж с отфильтрованным QuerySet и флагом использования различных поисковых запросов.
        """
        try:
            logger.info(f"Выполнен поиск задач по запросу '{search_term}' пользователем {request.user}")
            return super().get_search_results(request, queryset, search_term)
        except Exception as e:
            logger.log_exception(f"Ошибка при поиске задач: {str(e)}")
            return queryset, False

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Category.
    """
    list_display: Tuple[str, ...] = ('name',)

    def save_model(self, request: HttpRequest, obj: Category, form: Any, change: bool) -> None:
        """
        Сохраняет модель Category и логирует действие.

        Args:
            request (HttpRequest): Объект запроса.
            obj (Category): Объект категории.
            form (Any): Форма модели.
            change (bool): Флаг, указывающий на изменение существующей модели.

        Raises:
            ValidationError: Если возникла ошибка при сохранении модели.
        """
        try:
            action = "изменена" if change else "создана"
            super().save_model(request, obj, form, change)
            logger.info(f"Категория '{obj.name}' {action} пользователем {request.user}")
        except Exception as e:
            logger.log_exception(f"Ошибка при сохранении категории '{obj.name}': {str(e)}")
            raise ValidationError(f"Не удалось сохранить категорию: {str(e)}")

    def delete_model(self, request: HttpRequest, obj: Category) -> None:
        """
        Удаляет модель Category и логирует действие.

        Args:
            request (HttpRequest): Объект запроса.
            obj (Category): Объект категории.

        Raises:
            ValidationError: Если возникла ошибка при удалении модели.
        """
        try:
            name = obj.name
            super().delete_model(request, obj)
            logger.info(f"Категория '{name}' удалена пользователем {request.user}")
        except Exception as e:
            logger.log_exception(f"Ошибка при удалении категории '{obj.name}': {str(e)}")
            raise ValidationError(f"Не удалось удалить категорию: {str(e)}")

    def get_search_results(self, request: HttpRequest, queryset: QuerySet, search_term: str) -> Tuple[QuerySet, bool]:
        """
        Выполняет поиск по категориям и логирует действие.

        Args:
            request (HttpRequest): Объект запроса.
            queryset (QuerySet): Исходный QuerySet.
            search_term (str): Поисковый запрос.

        Returns:
            Tuple[QuerySet, bool]: Кортеж с отфильтрованным QuerySet и флагом использования различных поисковых запросов.
        """
        try:
            logger.info(f"Выполнен поиск категорий по запросу '{search_term}' пользователем {request.user}")
            return super().get_search_results(request, queryset, search_term)
        except Exception as e:
            logger.log_exception(f"Ошибка при поиске категорий: {str(e)}")
            return queryset, False