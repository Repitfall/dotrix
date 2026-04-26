from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.models import AccessNode, AccessRegistry
from api.v1.permissions import IsAdmin, CanViewRegistry
from api.v1.serializers.access_node import (
    AccessNodeModelSerializer,
    AccessNodeCreateInputSerializer,
    AccessNodeCreateOutputSerializer,
    AccessNodeUpdateInputSerializer
)
from api.v1.serializers.error import ErrorOutputSerializer
from api.v1.services.access_node import AccessNodeService
from api.v1.services.pagination import Pagination
from api.v1.filters.access_node import AccessNodeFilter


class AccessNodeViewSet(viewsets.GenericViewSet):
    """Управление узлами доступа"""

    pagination_class = Pagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AccessNodeFilter

    def get_queryset(self):
        """Начальный список для работы"""
        user = self.request.user

        if user.is_staff:
            return AccessNode.objects.filter(is_deleted=False)
        else:
            user_groups = user.access_groups.filter(is_deleted=False)
            registry_ids = AccessRegistry.objects.filter(
                groups__in=user_groups,
                is_deleted=False
            ).values_list('id', flat=True).distinct()

            return AccessNode.objects.filter(
                section__registry_id__in=registry_ids,
                is_deleted=False
            )

    def get_permissions(self):
        """Права на разные операции над узлами"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'restore']:
            return [IsAuthenticated(), IsAdmin()]
        else:
            return [IsAuthenticated(), CanViewRegistry()]

    @extend_schema(
        summary="Список узлов доступа",
        description="Возвращает список всех доступных узлов (с учетом прав)",
        responses={
            200: AccessNodeModelSerializer,
            401: ErrorOutputSerializer,
        },
        tags=['Узлы доступа']
    )
    def list(self, request):
        page = self.paginate_queryset(
            self.filter_queryset(
                self.get_queryset()))
        output_serializer = AccessNodeModelSerializer(
            page,
            many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(output_serializer.data)

    @extend_schema(
        summary="Просмотр узла доступа",
        description="Возвращает информацию о конкретном узле доступа",
        responses={
            200: AccessNodeModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Узлы доступа']
    )
    def retrieve(self, request, pk=None):
        node = get_object_or_404(self.get_queryset(), id=pk)
        output_serializer = AccessNodeModelSerializer(node)
        return Response(output_serializer.data)

    @extend_schema(
        summary="Создание узла доступа",
        description="Создает новый узел доступа",
        request=AccessNodeCreateInputSerializer,
        responses={
            201: AccessNodeCreateOutputSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer
        },
        tags=['Узлы доступа']
    )
    def create(self, request):
        input_serializer = AccessNodeCreateInputSerializer(
            data=request.data,
            context={'request': request}
        )
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        warnings = input_serializer.context.get('warnings', [])

        node, error = AccessNodeService.create_node(
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

        output_data = {
            'id': node.id,
            'name': node.name,
            'description': node.description,
            'ip': node.ip,
            'section_id': node.section_id,
            'ip_validated': node.ip_validated,
            'last_validation_error': node.last_validation_error
        }

        if warnings:
            output_data['warnings'] = warnings

        output_serializer = AccessNodeCreateOutputSerializer(output_data).data
        return Response(output_serializer, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Частичное обновление узла доступа",
        description="Обновляет часть данных узла доступа",
        request=AccessNodeUpdateInputSerializer,
        responses={
            200: AccessNodeModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Узлы доступа']
    )
    def partial_update(self, request, pk=None):
        node = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, node)

        input_serializer = AccessNodeUpdateInputSerializer(
            data=request.data,
            partial=True,
            context={'instance': node, 'request': request}
        )
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        warnings = input_serializer.context.get('warnings', [])

        updated_node, error = AccessNodeService.update_node(
            node, input_serializer.validated_data
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessNodeModelSerializer(updated_node).data

        if warnings:
            output_serializer['warnings'] = warnings

        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Полное обновление узла доступа",
        description="Обновляет все данные узла доступа",
        request=AccessNodeUpdateInputSerializer,
        responses={
            200: AccessNodeModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Узлы доступа']
    )
    def update(self, request, pk=None):
        node = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, node)

        input_serializer = AccessNodeUpdateInputSerializer(
            data=request.data,
            context={'instance': node, 'request': request}
        )
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        warnings = input_serializer.context.get('warnings', [])

        updated_node, error = AccessNodeService.update_node(
            node, input_serializer.validated_data
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessNodeModelSerializer(updated_node).data

        if warnings:
            output_serializer['warnings'] = warnings

        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Удаление узла доступа",
        description="Помечает узел доступа как удаленный",
        responses={
            204: OpenApiResponse(description="Успешное удаление"),
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Узлы доступа']
    )
    def destroy(self, request, pk=None):
        node = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, node)

        success, error = AccessNodeService.delete_node(node)

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
        summary="Восстановление узла доступа",
        description="Восстанавливает удаленный узел доступа",
        responses={
            200: AccessNodeModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Узлы доступа']
    )
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        node = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, node)

        success, error = AccessNodeService.restore_node(node)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка восстановления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessNodeModelSerializer(node).data
        return Response(output_serializer, status=status.HTTP_200_OK)
