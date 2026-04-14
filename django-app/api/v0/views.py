from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    ErrorOutputSerializer,
    StatusOutputSerializer,
    LoginInputSerializer,
    LoginOutputSerializer,
    ProfileOutputSerializer
)


class StatusView(APIView):
    """Проверка статуса сервера"""
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Проверка статуса сервера",
        description="Возвращает статус сервера. Используется для проверки работоспособности.",
        responses={
            200: OpenApiResponse(
                response=StatusOutputSerializer,
                description="Корректная работа сервера"
            )
        }
    )
    def get(self, request):
        output_serializer = StatusOutputSerializer({
            'status': 'ok'
        })
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Авторизация на сервере",
        description="""
        Авторизует пользователя и возвращает два JWT, позволяющие взаимодействовать с сервером.
        
        Access-токен используется для доступа к API
        Refresh-токен используется для получения нового Access-токена""",
        request=LoginInputSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginOutputSerializer,
                description="Успешная авторизация"
            ),
            400: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Некорректные данные"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Неверные учетные данные"
            ),
        }
    )
    def post(self, request):
        """Авторизация на сервере"""
        input_serializer = LoginInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            output_serializer = ErrorOutputSerializer({
                'error': "Некорректные данные",
                'detail': input_serializer.errors
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            username=input_serializer.validated_data['username'],
            password=input_serializer.validated_data['password']
        )

        if not user:
            output_serializer = ErrorOutputSerializer({
                'error': "Неправильные учетные данные",
                'detail': "Неправильный логин или пароль"
            })
            return Response(output_serializer.data, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            output_serializer = ErrorOutputSerializer({
                'error': "Аккаунт не активен",
                'detail': "Данный аккаунт отключен внутри системы"
            })
            return Response(output_serializer.data, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        output_serializer = LoginOutputSerializer({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_id': user.id,
            'login': user.username,
            'api_version': 'v0'
        })
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Просмотр своего профиля",
        description="Возвращает информацию о текущем авторизованном пользователе",
        request=LoginInputSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginOutputSerializer,
                description="Успешная авторизация"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Не авторизован"
            ),
        }
    )
    def get(self, request):
        """Просмотр своего профиля"""
        output_serializer = ProfileOutputSerializer(request.user)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
