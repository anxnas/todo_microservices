from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Task, Category
from .serializers import TaskCreateSerializer, TaskUpdateSerializer, CategorySerializer
from profi_log import MasterLogger

# Инициализация логгера
logger = MasterLogger("logs/views.log", level="DEBUG")
logger.setup_colored_console_logging()

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('user').prefetch_related('categories')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            logger.info(f"Используется TaskUpdateSerializer для действия {self.action}")
            return TaskUpdateSerializer
        logger.info(f"Используется TaskCreateSerializer для действия {self.action}")
        return TaskCreateSerializer

    def perform_create(self, serializer):
        logger.info(f"Создание новой задачи для пользователя {self.request.user}")
        serializer.save(user=self.request.user)

    def get_queryset(self):
        logger.info(f"Получение списка задач для пользователя {self.request.user}")
        return self.queryset.filter(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]