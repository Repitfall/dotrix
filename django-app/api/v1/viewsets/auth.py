from datetime import timedelta

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken
import rest_framework_simplejwt.token_blacklist as blacklist
from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.v1.serializers.error import ErrorOutputSerializer
from api.v1.serializers.auth import (
    LoginInputSerializer,
    LoginOutputSerializer,
    ChangePasswordSerializer
)
from api.v1.services.auth import AuthService


class LoginView(APIView):
    """Вход в учетную запись"""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Вход в учетную запись",
        description="Аутентифицирует пользователя и возвращает JWT-токены в httpOnly куки.",
        request=LoginInputSerializer,
        responses={
            200: LoginOutputSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
        },
        tags=['Аутентификация']
    )
    def post(self, request):
        """Обработка запроса на вход в учетную запись"""

        input_serializer = LoginInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        user, error = AuthService.authenticate_user(
            login=input_serializer.validated_data['login'],
            password=input_serializer.validated_data['password']
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка авторизации",
                    'detail': error
                }).data,
                status=status.HTTP_401_UNAUTHORIZED
            )

        tokens = AuthService.generate_tokens(user)

        output_serializer = LoginOutputSerializer({
            'id': user.id,
            'login': user.username
        }).data
        response = Response(output_serializer, status=status.HTTP_200_OK)
        response = AuthService.set_auth_cookies(response, tokens)
        return response


class LogoutView(APIView):
    """Выход из учетной записи"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Выход из учетной записи",
        description="Удаляет токены из куки и завершает сессию",
        responses={
            200: OpenApiResponse(
                description="Успешный выход"
            ),
            401: ErrorOutputSerializer,
        },
        tags=['Аутентификация']
    )
    def post(self, request):
        """Обработка запроса на выход из учетой записи"""

        response = Response({
            'message': "Успешный выход из системы"
        }, status=status.HTTP_200_OK)
        response = AuthService.clear_auth_cookies(response)
        return response


class RefreshTokenView(APIView):
    """Обновление access-токена"""

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="refresh_token",
        summary="Обновление access-токена",
        description="Использует refresh-токен из куки для получения нового access-токена",
        responses={
            200: OpenApiResponse(
                description="Успешный выход"
            ),
            401: ErrorOutputSerializer,
        },
        tags=['Аутентификация']
    )
    def post(self, request):
        """Обработка запроса на обновление access-токена"""

        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                ErrorOutputSerializer({
                    'error': "Отсутствует refresh-токен"
                }).data,
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)

            if blacklist.models.BlacklistedToken.objects.filter(
                    token__jti=refresh['jti']).exists():
                raise InvalidToken("Refresh-токен в чёрном списке")

            new_access_token = str(refresh.access_token)

            response = Response({
                'message': "Успешное обновление access-токена"
            }, status=status.HTTP_200_OK)
            response.set_cookie(
                'access_token',
                new_access_token,
                httponly=True,
                samesite='Strict',
                max_age=timedelta(minutes=30),
                path='/api/'
            )
            return response

        except InvalidToken:
            return Response(
                ErrorOutputSerializer({
                    'error': "Невалидный refresh-токен"
                }).data,
                status=status.HTTP_401_UNAUTHORIZED
            )


class ChangePasswordView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Смена пароля",
        description="Изменяет старый пароль на новый",
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="Успешная смена пароля"
            ),
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
        },
        tags=['Аутентификация']
    )
    def post(self, request):
        """Обработка запроса на изменение пароля"""

        input_serializer = ChangePasswordSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        user, error = AuthService.authenticate_user(
            login=input_serializer.validated_data['login'],
            password=input_serializer.validated_data['old_password'],
            change_password=True
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка авторизации",
                    'detail': error
                }).data,
                status=status.HTTP_401_UNAUTHORIZED
            )

        if input_serializer.validated_data['old_password'] == input_serializer.validated_data['new_password']:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка смены пароля",
                    'detail': "Новый пароль должен отличаться от старого"
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        success, error = AuthService.change_password(
            user, input_serializer.validated_data['new_password'])

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка смены пароля",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response(status=status.HTTP_200_OK)
        response = AuthService.clear_auth_cookies(response)
        return response
