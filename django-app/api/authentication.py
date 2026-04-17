from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):
    """Аутентификатор, извлекающий токен из httpOnly куки"""

    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None

        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except InvalidToken as error:
            raise AuthenticationFailed(str(error))
        except Exception as error:
            raise AuthenticationFailed(str(error))

    def get_validated_token(self, raw_token):
        return super().get_validated_token(raw_token)


class IsAdmin(permissions.BasePermission):
    """Аутентификатор, проверяющий на наличие роли администратора"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
