from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from api.models import User
from api.v1.permissions import IsAdmin, IsAdminOrReadOnly
from api.v1.serializers.error import ErrorOutputSerializer
from api.v1.serializers.user import (
    UserModelSerializer,
    UserCreateInputSerializer,
    UserCreateOutputSerializer,
    UserUpdateInputSerializer,
    UserFullUpdateInputSerializer,
)
from api.v1.services.user import UserService
from api.v1.services.pagination import Pagination
from api.v1.filters.users import UserFilter


class UserViewSet(viewsets.GenericViewSet):
    """Управление пользователями"""

    pagination_class = Pagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = UserFilter

    def get_queryset(self):
        """Начальный список для работы"""
        user = self.request.user

        if user.is_staff:
            return User.objects.all()
        else:
            return User.objects.filter(is_deleted=False)

    def get_permissions(self):
        """Права на разные операции над пользователями"""

        if self.action in ['create', 'update', 'partial_update', 'destroy', 'restore', 'reset_password']:
            return [IsAuthenticated(), IsAdmin()]
        else:
            return [AllowAny()]

    @extend_schema(
        summary="Список пользователей",
        description="Возвращает список всех пользователей (с учетом прав)",
        responses={
            200: UserModelSerializer,
            401: ErrorOutputSerializer,
        },
        tags=['Пользователи']
    )
    def list(self, request):
        page = self.paginate_queryset(
            self.filter_queryset(
                self.get_queryset()))
        output_serializer = UserModelSerializer(
            page,
            many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(output_serializer.data)

    @extend_schema(
        summary="Просмотр пользователя",
        description="Возвращает информацию о конкретном пользователе",
        responses={
            200: UserModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Пользователи']
    )
    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, user)
        output_serializer = UserModelSerializer(user)
        return Response(output_serializer.data)

    @extend_schema(
        summary="Создание пользователя",
        description="Создает нового пользователя",
        request=UserCreateInputSerializer,
        responses={
            201: UserCreateOutputSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer
        },
        tags=['Пользователи']
    )
    def create(self, request):
        input_serializer = UserCreateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        user, password, error = UserService.create_user(
            input_serializer.validated_data
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка создания",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = UserCreateOutputSerializer({
            'id': user.id,
            'login': user.username,
            'password': password,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'patronymic': user.patronymic,
            'post': user.post
        }).data

        return Response(output_serializer, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Обновление пользователя",
        description="Обновляет часть данных пользователя",
        request=UserUpdateInputSerializer,
        responses={
            200: UserModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Пользователи']
    )
    def partial_update(self, request, pk=None):
        user = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, user)

        input_serializer = UserUpdateInputSerializer(
            data=request.data, partial=True)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_user, error = UserService.update_user(
            user, input_serializer.validated_data)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = UserModelSerializer(updated_user).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Полное обновление пользователя",
        description="Обновляет все данные пользователя",
        request=UserFullUpdateInputSerializer,
        responses={
            200: UserModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Пользователи']
    )
    def update(self, request, pk=None):
        user = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, user)
        input_serializer = UserFullUpdateInputSerializer(
            data=request.data)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        updated_user, error = UserService.update_user(
            user, input_serializer.validated_data)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = UserModelSerializer(updated_user).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Удаление пользователя",
        description="Помечает пользователя как удаленного",
        responses={
            204: OpenApiResponse(
                description="Успешное удаление"
            ),
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Пользователи']
    )
    def destroy(self, request, pk=None):
        user = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, user)

        if user == request.user:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка удаления",
                    'detail': "Вы не можете удалить сами себя"
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        success, error = UserService.delete_user(user)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка удаления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Восстановление пользователя",
        description="Восстанавливает удаленного пользователя",
        responses={
            200: UserModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Пользователи']
    )
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        user = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, user)
        success, error = UserService.restore_user(user)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка восстановления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = UserModelSerializer(user).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Просмотр своего профиля",
        description="Возвращает информацию о текущем авторизованном пользователе",
        responses={
            200: UserModelSerializer,
            401: ErrorOutputSerializer
        },
        tags=['Пользователи']
    )
    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        output_serializer = UserModelSerializer(request.user).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Сброс пароля",
        description="Сбрасывает пароль пользователя и возвращает всю информацию о пользователе с новым паролем",
        responses={
            200: UserCreateOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Пользователи']
    )
    @action(detail=True, methods=['get'], url_path='reset_password')
    def reset_password(self, request, pk=None):
        user = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, user)

        password, error = UserService.reset_password(user)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка сброса пароля",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = UserCreateOutputSerializer({
            'id': user.id,
            'login': user.username,
            'password': password,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'patronymic': user.patronymic,
            'post': user.post
        }).data

        return Response(output_serializer, status=status.HTTP_200_OK)
