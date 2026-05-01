from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.models import AccessSection, AccessRegistry
from api.v1.permissions import IsAdmin, CanViewRegistry
from api.v1.serializers.access_section import (
    AccessSectionModelSerializer,
    AccessSectionCreateInputSerializer,
    AccessSectionCreateOutputSerializer,
    AccessSectionUpdateInputSerializer
)
from api.v1.serializers.error import ErrorOutputSerializer
from api.v1.services.access_section import AccessSectionService
from api.v1.services.pagination import Pagination
from api.v1.filters.access_section import AccessSectionFilter


class AccessSectionViewSet(viewsets.GenericViewSet):
    """Управление разделами доступа"""

    pagination_class = Pagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AccessSectionFilter

    def get_queryset(self):
        """Начальный список для работы"""
        user = self.request.user

        if user.is_staff:
            return AccessSection.objects.filter(is_deleted=False)
        else:
            user_groups = user.access_groups.filter(is_deleted=False)
            registry_ids = AccessRegistry.objects.filter(
                groups__in=user_groups,
                is_deleted=False
            ).values_list('id', flat=True).distinct()

            return AccessSection.objects.filter(
                registry_id__in=registry_ids,
                is_deleted=False
            )

    def get_permissions(self):
        """Права на разные операции над разделами"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'restore']:
            return [IsAuthenticated(), IsAdmin()]
        else:
            return [IsAuthenticated(), CanViewRegistry()]

    @extend_schema(
        summary="Список разделов доступа",
        description="Возвращает список всех доступных разделов (с учетом прав)",
        responses={
            200: AccessSectionModelSerializer,
            401: ErrorOutputSerializer,
        },
        tags=['Разделы доступа']
    )
    def list(self, request):
        page = self.paginate_queryset(
            self.filter_queryset(
                self.get_queryset()))
        output_serializer = AccessSectionModelSerializer(
            page,
            many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(output_serializer.data)

    @extend_schema(
        summary="Просмотр раздела доступа",
        description="Возвращает информацию о конкретном разделе доступа",
        responses={
            200: AccessSectionModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Разделы доступа']
    )
    def retrieve(self, request, pk=None):
        section = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, section)
        output_serializer = AccessSectionModelSerializer(section)
        return Response(output_serializer.data)

    @extend_schema(
        summary="Создание раздела доступа",
        description="Создает новый раздел доступа",
        request=AccessSectionCreateInputSerializer,
        responses={
            201: AccessSectionCreateOutputSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer
        },
        tags=['Разделы доступа']
    )
    def create(self, request):
        input_serializer = AccessSectionCreateInputSerializer(
            data=request.data)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        section, error = AccessSectionService.create_section(
            input_serializer.validated_data, request.user
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка создания",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessSectionCreateOutputSerializer({
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'registry_id': section.registry_id
        }).data

        return Response(output_serializer, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Частичное обновление раздела доступа",
        description="Обновляет часть данных раздела доступа",
        request=AccessSectionUpdateInputSerializer,
        responses={
            200: AccessSectionModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Разделы доступа']
    )
    def partial_update(self, request, pk=None):
        section = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, section)

        input_serializer = AccessSectionUpdateInputSerializer(
            instance=section,
            data=request.data,
            partial=True,
        )
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_section, error = AccessSectionService.update_section(
            section, input_serializer.validated_data, request.user
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessSectionModelSerializer(updated_section).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Полное обновление раздела доступа",
        description="Обновляет все данные раздела доступа",
        request=AccessSectionUpdateInputSerializer,
        responses={
            200: AccessSectionModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Разделы доступа']
    )
    def update(self, request, pk=None):
        section = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, section)

        input_serializer = AccessSectionUpdateInputSerializer(
            instance=section,
            data=request.data,
        )
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_section, error = AccessSectionService.update_section(
            section, input_serializer.validated_data, request.user
        )

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessSectionModelSerializer(updated_section).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Удаление раздела доступа",
        description="Помечает раздел доступа как удаленный",
        responses={
            204: OpenApiResponse(description="Успешное удаление"),
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Разделы доступа']
    )
    def destroy(self, request, pk=None):
        section = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, section)

        success, error = AccessSectionService.delete_section(
            section, request.user)

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
        summary="Восстановление раздела доступа",
        description="Восстанавливает удаленный раздел доступа",
        responses={
            200: AccessSectionModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Разделы доступа']
    )
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        section = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, section)

        success, error = AccessSectionService.restore_section(
            section, request.user)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка восстановления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessSectionModelSerializer(
            section, context=self.get_serializer_context()).data
        return Response(output_serializer, status=status.HTTP_200_OK)
