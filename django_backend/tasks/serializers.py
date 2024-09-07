from rest_framework import serializers
from typing import Dict, Any, List
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Task, Category
from django.conf import settings

logger = settings.LOGGER.get_logger('serializers')

class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.
    """
    class Meta:
        model = Category
        fields: List[str] = ['id', 'name']

class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания новых задач.
    """
    categories = CategorySerializer(many=True, required=False)

    class Meta:
        model = Task
        fields: List[str] = ['id', 'title', 'description', 'created_at', 'due_date', 'completed', 'user', 'categories']
        read_only_fields: List[str] = ['user']

    def create(self, validated_data: Dict[str, Any]) -> Task:
        """
        Создает новую задачу с связанными категориями.

        Args:
            validated_data (Dict[str, Any]): Валидированные данные для создания задачи.

        Returns:
            Task: Созданный объект задачи.

        Raises:
            ValidationError: Если возникла ошибка при создании задачи или категории.
        """
        try:
            categories_data: List[Dict[str, Any]] = validated_data.pop('categories', [])
            task = Task.objects.create(**validated_data)
            logger.info(f"Создана новая задача: {task.title}")

            for category_data in categories_data:
                category, created = Category.objects.get_or_create(**category_data)
                task.categories.add(category)
                if created:
                    logger.info(f"Создана новая категория: {category.name}")
                else:
                    logger.info(f"Использована существующая категория: {category.name}")

            return task
        except ValidationError as e:
            logger.log_exception(f"Ошибка валидации при создании задачи: {str(e)}")
        except Exception as e:
            logger.log_exception(f"Неожиданная ошибка при создании задачи: {str(e)}")

class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления существующих задач.
    """
    categories = CategorySerializer(many=True, required=False)
    title = serializers.CharField(required=False)

    class Meta:
        model = Task
        fields: List[str] = ['id', 'title', 'description', 'created_at', 'due_date', 'completed', 'user', 'categories']
        read_only_fields: List[str] = ['user']

    def update(self, instance: Task, validated_data: Dict[str, Any]) -> Task:
        """
        Обновляет существующую задачу и ее категории.

        Args:
            instance (Task): Существующий объект задачи для обновления.
            validated_data (Dict[str, Any]): Валидированные данные для обновления задачи.

        Returns:
            Task: Обновленный объект задачи.

        Raises:
            ValidationError: Если возникла ошибка при обновлении задачи или категории.
        """
        try:
            logger.info(f"Обновление задачи: {instance.title}")
            instance.title = validated_data.get('title', instance.title)
            instance.description = validated_data.get('description', instance.description)
            instance.due_date = validated_data.get('due_date', instance.due_date)
            instance.completed = validated_data.get('completed', instance.completed)

            categories_data: List[Dict[str, Any]] = validated_data.pop('categories', None)
            if categories_data is not None:
                instance.categories.clear()
                logger.info(f"Очищены все категории для задачи: {instance.title}")
                for category_data in categories_data:
                    category, created = Category.objects.get_or_create(**category_data)
                    instance.categories.add(category)
                    if created:
                        logger.info(f"Создана новая категория: {category.name}")
                    else:
                        logger.info(f"Использована существующая категория: {category.name}")

            instance.save()
            logger.info(f"Задача успешно обновлена: {instance.title}")
            return instance
        except ValidationError as e:
            logger.log_exception(f"Ошибка валидации при обновлении задачи: {str(e)}")
        except Exception as e:
            logger.log_exception(f"Неожиданная ошибка при обновлении задачи: {str(e)}")

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields: List[str] = ['id', 'username', 'email', 'password']

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Создает нового пользователя.

        Args:
            validated_data (Dict[str, Any]): Валидированные данные для создания пользователя.

        Returns:
            User: Созданный объект пользователя.

        Raises:
            ValidationError: Если возникла ошибка при создании пользователя.
        """
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data.get('email', ''),
                password=validated_data['password']
            )
            logger.info(f"Создан новый пользователь: {user.username}")
            return user
        except ValidationError as e:
            logger.log_exception(f"Ошибка валидации при создании пользователя: {str(e)}")
            raise
        except Exception as e:
            logger.log_exception(f"Неожиданная ошибка при создании пользователя: {str(e)}")
            raise