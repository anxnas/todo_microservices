from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.views import TaskViewSet, CategoryViewSet
from tasks.token import TokenPairView, Token2RefreshView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', Token2RefreshView.as_view(), name='token_refresh'),
]