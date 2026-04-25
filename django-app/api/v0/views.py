import secrets
import string
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from api.models import (
    User,
    AccessRegistry,
    AccessSection,
    AccessNode,
    AccessObject,
    AccessType
)
from api.authentication import IsAdmin
from .serializers import (
    ErrorOutputSerializer,
    StatusOutputSerializer,

    LoginInputSerializer,
    LoginOutputSerializer,

    UserInputSerializer,
    UserOutputSerializer,
    UserOutputListSerializer,
    CreateUserOutputSerializer,
    UserModelSerializer,

    AccessRegistryModelSerializer,
    AccessRegistryInputSerializer,
    AccessRegistryOutputSerializer,
    AccessRegistryOutputListSerializer,

    AccessSectionModelSerializer,
    AccessSectionInputSerializer,
    AccessSectionOutputSerializer,
    AccessSectionOutputListSerializer,

    AccessNodeModelSerializer,
    AccessNodeInputSerializer,
    AccessNodeOutputListSerializer,

    AccessObjectModelSerializer,
    AccessObjectInputSerializer,
    AccessObjectOutputListSerializer,

    AccessTypeModelSerializer,
    AccessTypeInputSerializer,
    AccessTypeOutputListSerializer,
)


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
                description="Пользователя не существует"
            ),
        }
    )
    def get(self, request, id):
        result = get_object_or_404(User, id=id)
        output_serializer = UserOutputSerializer({
            'id': result.id,
            'login': result.username,
            'last_name': result.last_name,
            'first_name': result.first_name,
            'patronymic': result.patronymic,
            'is_active': result.is_active
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
        parameters=[
            OpenApiParameter(
                name='page_size',
                description="Размер страницы пагинации",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=UserOutputListSerializer,
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
                response=CreateUserOutputSerializer,
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
        parameters=[
            OpenApiParameter(
                name='page_size',
                description="Размер страницы пагинации",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=AccessRegistryOutputListSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
        }
    )
    def get(self, request):
        result_list = AccessRegistry.objects.filter(is_deleted=False)

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
                response=AccessRegistryOutputSerializer,
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
            result = AccessRegistry.objects.create(
                name=input_serializer.validated_data['name']
            )
            output_serializer = AccessRegistryOutputSerializer({
                'id': result.id,
                'name': result.name
            })
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as error:
            output_serializer = ErrorOutputSerializer({
                'error': "Ошибка создания реестра доступа",
                'detail': str(error)
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)


class AccessRegistryView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        summary="Просмотр реестра доступа",
        description="""
        Возвращает информацию о конкретном реестре доступа.
        
        Доступно только с авторизацией.
        """,
        responses={
            200: OpenApiResponse(
                response=AccessRegistryOutputSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
            404: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Реестра доступа не существует"
            ),
        }
    )
    def get(self, request, id):
        result = get_object_or_404(AccessRegistry, id=id)

        output = {
            'id': result.id,
            'name': result.name,
        }
        if result.is_deleted:
            output['is_deleted'] = True
        output_serializer = AccessRegistryOutputSerializer(output)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Полное изменение реестра доступа",
        description="""
        Полностью изменяет реестр доступа и возвращает о нем информацию.
        
        Доступно только администраторам.
        """,
        request=AccessRegistryInputSerializer,
        responses={
            200: OpenApiResponse(
                response=AccessRegistryOutputSerializer,
                description="Успешный запрос"
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
            404: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Реестра доступа не существует"
            ),
        }
    )
    def put(self, request, id):
        result = get_object_or_404(AccessRegistry, id=id)
        input_serializer = AccessRegistryModelSerializer(
            result, data=request.data)

        if input_serializer.is_valid():
            result = input_serializer.save()
            output_serializer = AccessRegistryOutputSerializer({
                'id': result.id,
                'name': result.name
            })
            return Response(output_serializer.data, status=status.HTTP_200_OK)
        output_serializer = ErrorOutputSerializer({
            'error': "Некорректные данные",
            'detail': input_serializer.errors
        })
        return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Частичное изменение реестра доступа",
        description="""
        Частично изменяет реестр доступа и возвращает о нем информацию.
        
        Доступно только администраторам.
        """,
        request=AccessRegistryInputSerializer,
        responses={
            200: OpenApiResponse(
                response=AccessRegistryOutputSerializer,
                description="Успешный запрос"
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
            404: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Реестра доступа не существует"
            ),
        }
    )
    def patch(self, request, id):
        result = get_object_or_404(AccessRegistry, id=id)
        input_serializer = AccessRegistryModelSerializer(
            result, data=request.data, partial=True)

        if input_serializer.is_valid():
            result = input_serializer.save()
            output_serializer = AccessRegistryOutputSerializer({
                'id': result.id,
                'name': result.name
            })
            return Response(output_serializer.data, status=status.HTTP_200_OK)
        output_serializer = ErrorOutputSerializer({
            'error': "Некорректные данные",
            'detail': input_serializer.errors
        })
        return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Удаление реестра доступа",
        description="""
        Мягко удаляет реестр доступа из обычных списков.
        
        Доступно только администраторам.
        """,
        request=AccessRegistryInputSerializer,
        responses={
            204: OpenApiResponse(
                description="Успешный запрос"
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
            404: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Реестра доступа не существует"
            ),
        }
    )
    def delete(self, request, id):
        result = get_object_or_404(AccessRegistry, id=id)
        if result.is_deleted:
            output_serializer = ErrorOutputSerializer({
                'error': "Реестр данных уже удален"
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        result.is_deleted = True
        result.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccessRegistryRestoreView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Восстановление реестра доступа",
        description="""
        Восстанавливает реестр доступа для обычных списков.
        
        Доступно только администраторам.
        """,
        responses={
            200: OpenApiResponse(
                description="Успешный запрос"
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
            404: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Реестра доступа не существует"
            ),
        }
    )
    def post(self, request, id):
        result = get_object_or_404(AccessRegistry, id=id)
        if not result.is_deleted:
            output_serializer = ErrorOutputSerializer({
                'error': "Реестр данных уже не удален"
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        result.is_deleted = False
        result.save()
        output_serializer = AccessRegistryOutputSerializer({
            'id': result.id,
            'name': result.name
        })
        return Response(output_serializer.data, status=status.HTTP_200_OK)


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
        parameters=[
            OpenApiParameter(
                name='page_size',
                description="Размер страницы пагинации",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='registry',
                description="ID реестра доступа",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=AccessSectionOutputListSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
        }
    )
    def get(self, request):
        result_list = AccessSection.objects.filter(is_deleted=False)

        registry = request.query_params.get('registry')
        if registry:
            try:
                result_list = result_list.filter(registry=int(registry))
            except ValueError:
                output_serializer = ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': "registry должен быть целым числом"
                })
                return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100

        page = paginator.paginate_queryset(result_list, request)

        output_serializer = AccessSectionModelSerializer(page, many=True)

        return paginator.get_paginated_response(output_serializer.data)

    @extend_schema(
        summary="Создание нового раздела доступа",
        description="""
        Возвращает информацию о новом созданном разделе доступа.
        
        Доступно только администраторам.
        """,
        request=AccessSectionInputSerializer,
        responses={
            201: OpenApiResponse(
                response=AccessSectionOutputSerializer,
                description="Успешное создание раздела доступа"
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
        input_serializer = AccessSectionInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            output_serializer = ErrorOutputSerializer({
                'error': "Некорректные данные",
                'detail': input_serializer.errors
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = AccessSection.objects.create(
                registry=get_object_or_404(
                    AccessRegistry, id=input_serializer.validated_data['registry']),
                name=input_serializer.validated_data['name']
            )
            output_serializer = AccessSectionOutputSerializer({
                'id': result.id,
                'name': result.name
            })
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as error:
            output_serializer = ErrorOutputSerializer({
                'error': "Ошибка создания реестра доступа",
                'detail': str(error)
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)


class AccessSectionView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        summary="Просмотр раздела доступа",
        description="""
        Возвращает информацию о конкретном разделе доступа.
        
        Доступно только с авторизацией.
        """,
        responses={
            200: OpenApiResponse(
                response=AccessSectionOutputSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
            404: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Раздела доступа не существует"
            ),
        }
    )
    def get(self, request, id):
        result = get_object_or_404(AccessSection, id=id)
        output_serializer = AccessSectionOutputSerializer({
            'id': result.id,
            'name': result.name
        })
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Полное изменение раздела доступа",
        description="""
        Полностью изменяет раздел доступа и возвращает о нем информацию.
        
        Доступно только администраторам.
        """,
        request=AccessRegistryInputSerializer,
        responses={
            200: OpenApiResponse(
                response=AccessRegistryOutputSerializer,
                description="Успешный запрос"
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
            404: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Реестра доступа не существует"
            ),
        }
    )
    def put(self, request, id):
        result = get_object_or_404(AccessSection, id=id)
        input_serializer = AccessSectionModelSerializer(
            result, data=request.data)

        if input_serializer.is_valid():
            result = input_serializer.save()
            output_serializer = AccessSectionOutputSerializer({
                'id': result.id,
                'name': result.name
            })
            return Response(output_serializer.data, status=status.HTTP_200_OK)
        output_serializer = ErrorOutputSerializer({
            'error': "Некорректные данные",
            'detail': input_serializer.errors
        })
        return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)


class AccessNodeListView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        summary="Просмотр списка узлов доступов",
        description="""
        Возвращает информацию о всех узлах доступов.
        
        Доступно только с авторизацией.
        """,
        responses={
            200: OpenApiResponse(
                response=AccessNodeOutputListSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
        }
    )
    def get(self, request):
        result_list = AccessSection.objects.filter(is_deleted=False)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100

        page = paginator.paginate_queryset(result_list, request)

        output_serializer = AccessNodeModelSerializer(page, many=True)

        return paginator.get_paginated_response(output_serializer.data)

    @extend_schema(
        summary="Создание нового узла доступа",
        description="""
        Возвращает информацию о новом созданном узле доступа.
        
        Доступно только администраторам.
        """,
        request=AccessNodeInputSerializer,
        responses={
            201: OpenApiResponse(
                response=AccessSectionOutputSerializer,
                description="Успешное создание узла доступа"
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
        input_serializer = AccessNodeInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            output_serializer = ErrorOutputSerializer({
                'error': "Некорректные данные",
                'detail': input_serializer.errors
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = AccessNode.objects.create(
                registry=get_object_or_404(
                    AccessNode, id=input_serializer.validated_data['node']),
                name=input_serializer.validated_data['name']
            )
            output_serializer = AccessNodeOutputSerializer({
                'id': result.id,
                'name': result.name
            })
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as error:
            output_serializer = ErrorOutputSerializer({
                'error': "Ошибка создания реестра доступа",
                'detail': str(error)
            })
            return Response(output_serializer.data, status=status.HTTP_400_BAD_REQUEST)


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
                response=AccessObjectOutputListSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Нет авторизации"
            ),
        }
    )
    def get(self, request):
        result_list = AccessSection.objects.filter(is_deleted=False)

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
                response=AccessTypeOutputListSerializer,
                description="Успешный запрос"
            ),
            401: OpenApiResponse(
                response=ErrorOutputSerializer,
                description="Не авторизован"
            ),
        }
    )
    def get(self, request):
        result_list = AccessSection.objects.filter(is_deleted=False)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100

        page = paginator.paginate_queryset(result_list, request)

        output_serializer = AccessTypeModelSerializer(page, many=True)

        return paginator.get_paginated_response(output_serializer.data)
