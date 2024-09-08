from typing import Dict, Any
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status

logger = settings.LOGGER.get_logger('token')

class TokenSerializer(TokenObtainPairSerializer):
    """
    Сериализатор для получения пары токенов с дополнительной информацией о пользователе.
    """
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидирует атрибуты и добавляет user_id к данным токена.

        Args:
            attrs (Dict[str, Any]): Атрибуты для валидации.

        Returns:
            Dict[str, Any]: Валидированные данные с добавленным user_id.

        Raises:
            Exception: Если произошла ошибка при валидации.
        """
        try:
            data = super().validate(attrs)
            data['user_id'] = self.user.id
            logger.info(f"Токен успешно создан для пользователя {self.user.username}")
            return data
        except AuthenticationFailed as e:
            logger.warning(f"Неудачная попытка аутентификации: {str(e)}")
            raise  # Перебрасываем исключение для обработки в представлении
        except Exception as e:
            logger.log_exception(f"Ошибка при создании токена: {str(e)}")
            raise

class TokenPairView(TokenObtainPairView):
    """
    Представление для получения пары токенов.
    """
    serializer_class = TokenSerializer

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для получения токенов.

        Args:
            request: HTTP-запрос.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: HTTP-ответ с токенами или сообщением об ошибке.
        """
        try:
            response = super().post(request, *args, **kwargs)
            logger.info("Успешный запрос на получение токенов")
            return response
        except AuthenticationFailed as e:
            logger.warning(f"Неудачная попытка аутентификации: {str(e)}")
            return Response(
                {"error": "Неверные учетные данные. Пожалуйста, проверьте логин и пароль."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.log_exception(f"Ошибка при обработке запроса на получение токенов: {str(e)}")
            return Response({"error": "Произошла внутренняя ошибка сервера."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Token2RefreshSerializer(TokenRefreshSerializer):
    """
    Сериализатор для обновления токена с дополнительной информацией о пользователе.
    """
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидирует атрибуты и добавляет user_id к обновленным данным токена.

        Args:
            attrs (Dict[str, Any]): Атрибуты для валидации.

        Returns:
            Dict[str, Any]: Валидированные данные с добавленным user_id.

        Raises:
            Exception: Если произошла ошибка при валидации.
        """
        try:
            data = super().validate(attrs)
            refresh = RefreshToken(attrs['refresh'])
            data['user_id'] = refresh['user_id']
            logger.info(f"Токен успешно обновлен для пользователя {refresh['user_id']}")
            return data
        except Exception as e:
            logger.log_exception(f"Ошибка при обновлении токена: {str(e)}")
            raise  # Перебрасываем исключение для обработки в представлении

class Token2RefreshView(TokenRefreshView):
    """
    Представление для обновления токена.
    """
    serializer_class = Token2RefreshSerializer

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для обновления токена.

        Args:
            request: HTTP-запрос.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: HTTP-ответ с обновленным токеном или сообщением об ошибке.
        """
        try:
            response = super().post(request, *args, **kwargs)
            logger.info("Успешный запрос на обновление токена")
            return response
        except Exception as e:
            logger.log_exception(f"Ошибка при обработке запроса на обновление токена: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)