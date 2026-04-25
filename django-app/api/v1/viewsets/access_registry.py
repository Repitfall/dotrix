from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.models import AccessRegistry
from api.v1.permissions import IsAdmin, IsAdminOrReadOnly, CanViewRegistry
from api.v1.serializers.access_registry import (
    AccessRegistryModelSerializer,
    AccessRegistryCreateInputSerializer,
    AccessRegistryUpdateInputSerializer,
    AccessRegistryFullUpdateInputSerializer,
    AccessRegistryCreateOutputSerializer
)
from api.v1.serializers.error import ErrorOutputSerializer
from api.v1.services.access_registry import AccessRegistryService
from api.v1.services.pagination import Pagination
from api.v1.filters.access_registry import AccessRegistryFilter


class AccessRegistryViewSet(viewsets.GenericViewSet):
    """Управление реестрами доступа"""

    pagination_class = Pagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AccessRegistryFilter

    def get_queryset(self):
        """Начальный список для работы"""
        user = self.request.user

        if user.is_staff:
            return AccessRegistry.objects.all()
        else:
            user_groups = user.access_groups.filter(is_deleted=False)
            return AccessRegistry.objects.filter(
                groups__in=user_groups,
                is_deleted=False
            ).distinct()

    def get_permissions(self):
        """Права на разные операции над реестрами доступа"""

        if self.action in ['create', 'update', 'partial_update', 'destroy', 'restore']:
            return [IsAuthenticated(), IsAdmin()]
        else:
            return [IsAuthenticated(), CanViewRegistry()]

    @extend_schema(
        summary="Список реестров доступа",
        description="Возвращает список всех доступных реестров (с учетом прав)",
        responses={
            200: AccessRegistryModelSerializer,
            401: ErrorOutputSerializer,
        },
        tags=['Реестры доступа']
    )
    def list(self, request):
        page = self.paginate_queryset(
            self.filter_queryset(
                self.get_queryset()))
        output_serializer = AccessRegistryModelSerializer(
            page,
            many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(output_serializer.data)

    @extend_schema(
        summary="Просмотр реестра доступа",
        description="Возвращает информацию о конкретном реестре доступа",
        responses={
            200: AccessRegistryModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Реестры доступа']
    )
    def retrieve(self, request, pk=None):
        registry = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, registry)
        output_serializer = AccessRegistryModelSerializer(registry)
        return Response(output_serializer.data)

    @extend_schema(
        summary="Создание реестра доступа",
        description="Создает новый реестр доступа и возвращает о нем информацию",
        request=AccessRegistryCreateInputSerializer,
        responses={
            201: AccessRegistryCreateOutputSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer
        },
        tags=['Реестры доступа']
    )
    def create(self, request):
        input_serializer = AccessRegistryCreateInputSerializer(
            data=request.data)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        registry, error = AccessRegistryService.create_registry(
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

        output_serializer = AccessRegistryCreateOutputSerializer({
            'id': registry.id,
            'name': registry.name,
            'description': registry.description,
            'owner_group_ids': list(registry.owner_groups.values_list(
                'id', flat=True))
        }).data

        return Response(output_serializer, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Обновление реестра доступа",
        description="Обновляет часть данных реестра доступа",
        request=AccessRegistryUpdateInputSerializer,
        responses={
            200: AccessRegistryModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Реестры доступа']
    )
    def partial_update(self, request, pk=None):
        registry = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, registry)

        input_serializer = AccessRegistryUpdateInputSerializer(
            data=request.data,
            partial=True
        )
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_registry, error = AccessRegistryService.update_registry(
            registry, input_serializer.validated_data
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessRegistryModelSerializer(
            updated_registry).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Полное обновление реестра доступа",
        description="Обновляет все данные реестра доступа",
        request=AccessRegistryFullUpdateInputSerializer,
        responses={
            200: AccessRegistryModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Реестры доступа']
    )
    def update(self, request, pk=None):
        registry = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, registry)

        input_serializer = AccessRegistryFullUpdateInputSerializer(
            data=request.data
        )
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_registry, error = AccessRegistryService.update_registry(
            registry, input_serializer.validated_data
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessRegistryModelSerializer(
            updated_registry).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Удаление реестра доступа",
        description="Помечает реестр доступа как удаленный",
        responses={
            204: OpenApiResponse(description="Успешное удаление"),
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Реестры доступа']
    )
    def destroy(self, request, pk=None):
        registry = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, registry)

        success, error = AccessRegistryService.delete_registry(registry)

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
        summary="Восстановление реестра доступа",
        description="Восстанавливает удаленный реестр доступа",
        responses={
            200: AccessRegistryModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Реестры доступа']
    )
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        registry = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, registry)

        success, error = AccessRegistryService.restore_registry(registry)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка восстановления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessRegistryModelSerializer(registry).data
        return Response(output_serializer, status=status.HTTP_200_OK)
