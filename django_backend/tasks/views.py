from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from .models import Task, Category
from .serializers import TaskCreateSerializer, TaskUpdateSerializer, CategorySerializer, UserSerializer

logger = settings.LOGGER.get_logger('views')

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления задачами.
    Предоставляет CRUD операции для задач пользователя.
    """
    queryset = Task.objects.select_related('user').prefetch_related('categories')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        """
        if self.action in ['update', 'partial_update']:
            logger.info(f"Используется TaskUpdateSerializer для действия {self.action}")
            return TaskUpdateSerializer
        logger.info(f"Используется TaskCreateSerializer для действия {self.action}")
        return TaskCreateSerializer

    def perform_create(self, serializer):
        """
        Создает новую задачу для текущего пользователя.
        """
        try:
            logger.info(f"Создание новой задачи для пользователя {self.request.user}")
            serializer.save(user=self.request.user)
        except Exception as e:
            logger.log_exception(f"Ошибка при создании задачи для пользователя {self.request.user}")

    def get_queryset(self):
        """
        Возвращает queryset задач текущего пользователя.
        """
        logger.info(f"Получение списка задач для пользователя {self.request.user}")
        return self.queryset.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Возвращает список задач пользователя.
        """
        try:
            logger.info(f"Запрос списка задач от пользователя {request.user}")
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.log_exception(f"Ошибка при получении списка задач для пользователя {request.user}")
            return Response({"error": "Произошла ошибка при получении списка задач"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Возвращает детальную информацию о задаче.
        """
        try:
            logger.info(f"Запрос детальной информации о задаче от пользователя {request.user}")
            return super().retrieve(request, *args, **kwargs)
        except ObjectDoesNotExist:
            logger.log_exception(f"Задача не найдена для пользователя {request.user}")
            return Response({"error": "Задача не найдена"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.log_exception(f"Ошибка при получении информации о задаче для пользователя {request.user}")
            return Response({"error": "Произошла ошибка при получении информации о задаче"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """
        Обновляет задачу.
        """
        try:
            logger.info(f"Обновление задачи пользователем {request.user}")
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.log_exception(f"Ошибка при обновлении задачи пользователем {request.user}")
            return Response({"error": "Произошла ошибка при обновлении задачи"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет задачу.
        """
        try:
            logger.info(f"Удаление задачи пользователем {request.user}")
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.log_exception(f"Ошибка при удалении задачи пользователем {request.user}")
            return Response({"error": "Произошла ошибка при удалении задачи"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления категориями.
    Предоставляет CRUD операции для категорий.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Возвращает список категорий.
        """
        try:
            logger.info(f"Запрос списка категорий от пользователя {request.user}")
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.log_exception(f"Ошибка при получении списка категорий для пользователя {request.user}")
            return Response({"error": "Произошла ошибка при получении списка категорий"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Возвращает детальную информацию о категории.
        """
        try:
            logger.info(f"Запрос детальной информации о категории от пользователя {request.user}")
            return super().retrieve(request, *args, **kwargs)
        except ObjectDoesNotExist:
            logger.log_exception(f"Категория не найдена для пользователя {request.user}")
            return Response({"error": "Категория не найдена"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.log_exception(f"Ошибка при получении информации о категории для пользователя {request.user}")
            return Response({"error": "Произошла ошибка при получении информации о категории"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """
        Создает новую категорию.
        """
        try:
            logger.info(f"Создание новой категории пользователем {request.user}")
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.log_exception(f"Ошибка при создании категории пользователем {request.user}")
            return Response({"error": "Произошла ошибка при создании категории"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """
        Обновляет категорию.
        """
        try:
            logger.info(f"Обновление категории пользователем {request.user}")
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.log_exception(f"Ошибка при обновлении категории пользователем {request.user}")
            return Response({"error": "Произошла ошибка при обновлении категории"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет категорию.
        """
        try:
            logger.info(f"Удаление категории пользователем {request.user}")
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.log_exception(f"Ошибка при удалении категории пользователем {request.user}")
            return Response({"error": "Произошла ошибка при удалении категории"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateUserView(generics.CreateAPIView):
    """
    Представление для создания нового пользователя.
    Доступно только для администраторов.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        """
        Создает нового пользователя.
        """
        try:
            logger.info(f"Попытка создания нового пользователя администратором {request.user}")
            response = super().create(request, *args, **kwargs)
            logger.info(f"Пользователь успешно создан администратором {request.user}")
            return response
        except Exception as e:
            logger.log_exception(f"Ошибка при создании пользователя администратором {request.user}: {str(e)}")
            return Response(
                {"error": "Произошла ошибка при создании пользователя"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )