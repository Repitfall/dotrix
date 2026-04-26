from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from datetime import timedelta
from django.conf import settings


class AuthService:
    """Сервис для работы с авторизацией"""

    @staticmethod
    def authenticate_user(login: str, password: str, change_password: bool = False) -> tuple:
        """Аутентифицирует пользователя"""

        user = authenticate(username=login, password=password)

        if not user:
            return None, "Неправильные учетные данные"

        if not user.is_active:
            return None, "Учетная запись отключена. Обратитесь к администратору."

        if user.reset_password and not change_password:
            return None, "Учетная запись отключена. Сбросьте свой пароль для активации."

        return user, None

    @staticmethod
    def generate_tokens(user) -> dict:
        """Генерирует JWT-токены для пользователя"""

        refresh = RefreshToken.for_user(user)

        access_lifetime = getattr(settings, 'JWT_ACCESS_LIFETIME', 30)
        refresh_lifetime = getattr(settings, 'JWT_REFRESH_LIFETIME', 8)

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'access_expires': timedelta(minutes=access_lifetime),
            'refresh_expires': timedelta(hours=refresh_lifetime),
        }

    @staticmethod
    def set_auth_cookies(response, tokens: dict):
        """Устанавливает httpOnly куки с токенами"""

        response.set_cookie(
            'access_token',
            tokens['access'],
            httponly=True,
            samesite='Strict',
            max_age=tokens['access_expires'],
            path='/api/'
        )
        response.set_cookie(
            'refresh_token',
            tokens['refresh'],
            httponly=True,
            samesite='Strict',
            max_age=tokens['refresh_expires'],
            path='/api/'
        )

        return response

    @staticmethod
    def clear_auth_cookies(response):
        """Удаляет куки с токенами"""

        response.delete_cookie('access_token', path='/api/')
        response.delete_cookie('refresh_token', path='/api/')
        return response

    @staticmethod
    def change_password(user, password):
        """Смена пароля пользователя"""

        if not user.is_active:
            return False, "Пользователь должен быть активен"
        if not password:
            return False, "Пароль не может быть пустым"
        user.set_password(password)
        user.reset_password = False
        user.save()

        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        return True, None
