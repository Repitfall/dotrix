import secrets
import string
from datetime import timedelta

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiTypes
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from api.models import User, AccessRegistry, AccessSection, AccessNode, AccessObject, AccessType
from .serializers import (
    ErrorOutputSerializer,
    StatusOutputSerializer,
    LoginInputSerializer,
    LoginOutputSerializer,
    UserInputSerializer,
    UserOutputSerializer,
    CreateUserOutputSerializer,
    UserModelSerializer,
    ListOutputSerializer,
    AccessRegistryModelSerializer,
    AccessRegistryInputSerializer,
    AccessRegistryOutputSerializer,
    AccessSectionModelSerializer,
    AccessNodeModelSerializer,
    AccessObjectModelSerializer,
    AccessTypeModelSerializer
)
from api.authentication import IsAdmin


class StatusView(APIView):
    """Проверка статуса сервера"""
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Проверка статуса сервера",
        description="""
        Возвращает статус сервера. Используется для проверки работоспособности.
        
        Доступно без авторизации.
        """,
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
        Авторизует пользователя и возвращает два JWT в HttpOnly Cookie, позволяющие взаимодействовать с сервером.
        
        Access-токен используется для доступа к API.
        Refresh-токен используется для получения нового Access-токена.
        
        Доступно без авторизации.
        """,
        request=LoginInputSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginOutputSerializer,
                description="Успешная авторизация",
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
            username=input_serializer.validated_data['login'],
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

        refresh_token = RefreshToken.for_user(user)
        output_serializer = LoginOutputSerializer({
            'id': user.id,
            'login': user.username
        })
        output = Response(output_serializer.data, status=status.HTTP_200_OK)
        output.set_cookie(
            'access_token',
            str(refresh_token.access_token),
            httponly=True,
            samesite='Strict',
            max_age=timedelta(minutes=30)    # 30 минут
        )
        output.set_cookie(
            'refresh_token',
            str(refresh_token),
            httponly=True,
            samesite='Strict',
            max_age=timedelta(hours=8)   # 8 часов
        )
        return output


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Просмотр своего профиля",
        description="""
        Возвращает информацию о текущем авторизованном пользователе.
        
        Доступно только с авторизацией.
        """,
        responses={
            200: OpenApiResponse(
                response=LoginOutputSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
        }
    )
    def get(self, request):
        """Просмотр своего профиля"""
        user = request.user
        output_serializer = UserOutputSerializer({
            'id': user.id,
            'login': user.username
        })
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class UserView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        summary="Просмотр пользователя",
        description="""
        Возвращает информацию о конкретном пользователе.
        
        Доступно только с авторизацией.
        """,
        responses={
            200: OpenApiResponse(
                response=UserOutputSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
            404: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Доступ запрещен"
            ),
        }
    )
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        output_serializer = UserOutputSerializer({
            'id': user.id,
            'login': user.username,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'patronymic': user.patronymic,
            'is_active': user.is_active
        })
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class UserListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        summary="Просмотр списка пользователей",
        description="""
        Возвращает информацию о всех пользователях.
        
        Доступно только с авторизацией.
        """,
        responses={
            200: OpenApiResponse(
                response=ListOutputSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
        }
    )
    def get(self, request):
        result_list = User.objects.all()

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100

        page = paginator.paginate_queryset(result_list, request)

        output_serializer = UserModelSerializer(page, many=True)

        return paginator.get_paginated_response(output_serializer.data)

    @extend_schema(
        summary="Создание нового пользователя",
        description="""
        Возвращает информацию о новом созданном пользователе.
        
        Доступно только администраторам.
        """,
        request=UserInputSerializer,
        responses={
            201: OpenApiResponse(
                response=ListOutputSerializer,
                description="Успешное создание профиля"
            ),
            400: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Некорректные данные"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
            403: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Доступ запрещен"
            ),
        }
    )
    def post(self, request):
        input_serializer = UserInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            output_serializer = ErrorOutputSerializer({
                'error': "Некорректные данные",
                'detail': input_serializer.errors
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)

        generated_password = ''.join(secrets.choice(
            string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(12))

        try:
            user = User.objects.create_user(
                username=input_serializer.validated_data['login'],
                password=generated_password,
                last_name=input_serializer.validated_data.get('last_name', ''),
                first_name=input_serializer.validated_data.get(
                    'first_name', '')
            )
            output_serializer = CreateUserOutputSerializer({
                'id': user.id,
                'login': user.username,
                'password': generated_password,
                'last_name': user.last_name,
                'first_name': user.first_name,
                'patronymic': user.patronymic
            })
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as error:
            output_serializer = ErrorOutputSerializer({
                'error': "Ошибка создания профиля",
                'detail': str(error)
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)


class AccessRegistryListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        summary="Просмотр списка реестров доступов",
        description="""
        Возвращает информацию о всех реестрах доступов.
        
        Доступно только с авторизацией.
        """,
        responses={
            200: OpenApiResponse(
                response=ListOutputSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
        }
    )
    def get(self, request):
        result_list = AccessRegistry.objects.all()

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100

        page = paginator.paginate_queryset(result_list, request)

        output_serializer = AccessRegistryModelSerializer(page, many=True)

        return paginator.get_paginated_response(output_serializer.data)

    @extend_schema(
        summary="Создание нового реестра доступа",
        description="""
        Возвращает информацию о новом созданном реестре доступа.
        
        Доступно только администраторам.
        """,
        request=AccessRegistryInputSerializer,
        responses={
            201: OpenApiResponse(
                response=ListOutputSerializer,
                description="Успешное создание реестра доступа"
            ),
            400: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Некорректные данные"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
            403: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Доступ запрещен"
            ),
        }
    )
    def post(self, request):
        input_serializer = AccessRegistryInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            output_serializer = ErrorOutputSerializer({
                'error': "Некорректные данные",
                'detail': input_serializer.errors
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_object = AccessRegistry.objects.create(
                name=input_serializer.validated_data['name']
            )
            output_serializer = AccessRegistryOutputSerializer({
                'id': new_object.id,
                'name': new_object.name
            })
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as error:
            output_serializer = ErrorOutputSerializer({
                'error': "Ошибка создания реестра доступа",
                'detail': str(error)
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)


class AccessSectionListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        summary="Просмотр списка разделов доступов",
        description="""
        Возвращает информацию о всех разделах доступов.
        
        Доступно только с авторизацией.
        """,
        responses={
            200: OpenApiResponse(
                response=ListOutputSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
        }
    )
    def get(self, request):
        result_list = AccessSection.objects.all()

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100

        page = paginator.paginate_queryset(result_list, request)

        output_serializer = AccessSectionModelSerializer(page, many=True)

        return paginator.get_paginated_response(output_serializer.data)


class AccessNodeListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        summary="Просмотр списка реестров доступов",
        description="""
        Возвращает информацию о всех реестрах доступов.
        
        Доступно только с авторизацией.
        """,
        responses={
            200: OpenApiResponse(
                response=ListOutputSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
        }
    )
    def get(self, request):
        result_list = AccessSection.objects.all()

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100

        page = paginator.paginate_queryset(result_list, request)

        output_serializer = AccessNodeModelSerializer(page, many=True)

        return paginator.get_paginated_response(output_serializer.data)


class AccessObjectListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        summary="Просмотр списка объектов доступов",
        description="""
        Возвращает информацию о всех объектов доступов.
        
        Доступно только с авторизацией.
        """,
        responses={
            200: OpenApiResponse(
                response=ListOutputSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
        }
    )
    def get(self, request):
        result_list = AccessSection.objects.all()

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100

        page = paginator.paginate_queryset(result_list, request)

        output_serializer = AccessObjectModelSerializer(page, many=True)

        return paginator.get_paginated_response(output_serializer.data)


class AccessTypeListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        summary="Просмотр списка типов доступов",
        description="""
        Возвращает информацию о всех типах доступов.
        
        Доступно только с авторизацией.
        """,
        responses={
            200: OpenApiResponse(
                response=ListOutputSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Не авторизован"
            ),
        }
    )
    def get(self, request):
        result_list = AccessSection.objects.all()

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100

        page = paginator.paginate_queryset(result_list, request)

        output_serializer = AccessTypeModelSerializer(page, many=True)

        return paginator.get_paginated_response(output_serializer.data)
