from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.models import AccessObject, AccessRegistry
from api.v1.permissions import IsAdmin, CanViewRegistry
from api.v1.serializers.access_object import (
    AccessObjectModelSerializer,
    AccessObjectCreateInputSerializer,
    AccessObjectCreateOutputSerializer,
    AccessObjectUpdateInputSerializer
)
from api.v1.serializers.error import ErrorOutputSerializer
from api.v1.services.access_object import AccessObjectService
from api.v1.services.pagination import Pagination
from api.v1.filters.access_object import AccessObjectFilter


class AccessObjectViewSet(viewsets.GenericViewSet):
    """Управление объектами доступа"""

    pagination_class = Pagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AccessObjectFilter

    def get_queryset(self):
        """Начальный список для работы"""
        user = self.request.user

        if user.is_staff:
            return AccessObject.objects.filter(is_deleted=False)
        else:
            user_groups = user.access_groups.filter(is_deleted=False)
            registry_ids = AccessRegistry.objects.filter(
                groups__in=user_groups,
                is_deleted=False
            ).values_list('id', flat=True).distinct()

            return AccessObject.objects.filter(
                node__section__registry_id__in=registry_ids,
                is_deleted=False
            )

    def get_permissions(self):
        """Права на разные операции над объектами"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'restore']:
            return [IsAuthenticated(), IsAdmin()]
        else:
            return [IsAuthenticated(), CanViewRegistry()]

    @extend_schema(
        summary="Список объектов доступа",
        description="Возвращает список всех доступных объектов (с учетом прав)",
        responses={
            200: AccessObjectModelSerializer,
            401: ErrorOutputSerializer
        },
        tags=['Объекты доступа']
    )
    def list(self, request):
        page = self.paginate_queryset(
            self.filter_queryset(
                self.get_queryset()))
        serializer = AccessObjectModelSerializer(
            page,
            many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Просмотр объекта доступа",
        description="Возвращает информацию о конкретном объекте доступа",
        responses={
            200: AccessObjectModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Объекты доступа']
    )
    def retrieve(self, request, pk=None):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, obj)
        output_serializer = AccessObjectModelSerializer(
            obj, context=self.get_serializer_context()).data
        return Response(output_serializer)

    @extend_schema(
        summary="Создание объекта доступа",
        description="Создает новый объект доступа",
        request=AccessObjectCreateInputSerializer,
        responses={
            201: AccessObjectCreateOutputSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer
        },
        tags=['Объекты доступа']
    )
    def create(self, request):
        input_serializer = AccessObjectCreateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        obj, error = AccessObjectService.create_object(
            input_serializer.validated_data, request.user)
        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка создания",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessObjectCreateOutputSerializer({
            'id': obj.id,
            'name': obj.name,
            'description': obj.description,
            'resource_path': obj.resource_path,
            'node_id': obj.node_id
        }).data
        return Response(output_serializer, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Частичное обновление объекта доступа",
        description="Обновляет часть данных объекта доступа",
        request=AccessObjectUpdateInputSerializer,
        responses={
            200: AccessObjectModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Объекты доступа']
    )
    def partial_update(self, request, pk=None):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, obj)

        input_serializer = AccessObjectUpdateInputSerializer(
            instance=obj,
            data=request.data,
            partial=True,
            context=self.get_serializer_context()
        )
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_obj, error = AccessObjectService.update_object(
            obj, input_serializer.validated_data, request.user)
        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AccessObjectModelSerializer(updated_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Полное обновление объекта доступа",
        description="Обновляет все данные объекта доступа",
        request=AccessObjectUpdateInputSerializer,
        responses={
            200: AccessObjectModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Объекты доступа']
    )
    def update(self, request, pk=None):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, obj)

        input_serializer = AccessObjectUpdateInputSerializer(
            instance=obj,
            data=request.data,
            context=self.get_serializer_context()
        )
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_obj, error = AccessObjectService.update_object(
            obj, input_serializer.validated_data, request.user)
        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AccessObjectModelSerializer(updated_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Удаление объекта доступа",
        description="Помечает объект доступа как удаленный",
        responses={
            204: OpenApiResponse(description="Успешное удаление"),
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Объекты доступа']
    )
    def destroy(self, request, pk=None):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, obj)

        success, error = AccessObjectService.delete_object(obj, request.user)

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
        summary="Восстановление объекта доступа",
        description="Восстанавливает удаленный объект доступа",
        responses={
            200: AccessObjectModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Объекты доступа']
    )
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        obj = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, obj)

        success, error = AccessObjectService.restore_object(obj, request.user)
        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка восстановления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessObjectModelSerializer(
            obj, context=self.get_serializer_context()).data
        return Response(output_serializer, status=status.HTTP_200_OK)
