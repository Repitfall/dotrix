from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.models import AccessType, AccessRegistry
from api.v1.permissions import IsAdmin, CanViewRegistry
from api.v1.serializers.access_type import (
    AccessTypeModelSerializer,
    AccessTypeCreateInputSerializer,
    AccessTypeCreateOutputSerializer,
)
from api.v1.serializers.error import ErrorOutputSerializer
from api.v1.services.access_type import AccessTypeService
from api.v1.services.pagination import Pagination
from api.v1.filters.access_type import AccessTypeFilter


class AccessTypeViewSet(viewsets.GenericViewSet):
    """Управление типами доступа (AccessType)"""

    pagination_class = Pagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AccessTypeFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AccessType.objects.all()
        else:
            user_groups = user.access_groups.filter(is_deleted=False)
            registry_ids = AccessRegistry.objects.filter(
                groups__in=user_groups,
            ).values_list('id', flat=True).distinct()

            return AccessType.objects.filter(
                object__node__section__registry_id__in=registry_ids, is_deleted=False
            )

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'restore']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), CanViewRegistry()]

    @extend_schema(
        summary="Список типов доступа",
        responses={
            200: AccessTypeModelSerializer,
            401: ErrorOutputSerializer
        },
        tags=['Типы доступа']
    )
    def list(self, request):
        page = self.paginate_queryset(
            self.filter_queryset(self.get_queryset()))
        serializer = AccessTypeModelSerializer(
            page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Просмотр типа доступа",
        responses={
            200: AccessTypeModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Типы доступа']
    )
    def retrieve(self, request, pk=None):
        access_type = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, access_type)
        serializer = AccessTypeModelSerializer(
            access_type, context=self.get_serializer_context())
        return Response(serializer.data)

    @extend_schema(
        summary="Создание типа доступа",
        request=AccessTypeCreateInputSerializer,
        responses={
            201: AccessTypeCreateOutputSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer
        },
        tags=['Типы доступа']
    )
    def create(self, request):
        input_serializer = AccessTypeCreateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        access_type, error = AccessTypeService.create_access_type(
            input_serializer.validated_data, request.user)
        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка создания",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessTypeCreateOutputSerializer({
            'id': access_type.id,
            'object_id': access_type.object_id,
            'template_id': access_type.template_id
        }).data
        return Response(output_serializer, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Удаление типа доступа",
        responses={
            204: OpenApiResponse(description="Успешное удаление"),
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Типы доступа']
    )
    def destroy(self, request, pk=None):
        access_type = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, access_type)

        success, error = AccessTypeService.delete_access_type(
            access_type, request.user)

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
        summary="Восстановление типа доступа",
        responses={
            200: AccessTypeModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Типы доступа']
    )
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        access_type = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, access_type)

        success, error = AccessTypeService.restore_access_type(
            access_type, request.user)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка восстановления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessTypeModelSerializer(
            access_type, context=self.get_serializer_context()).data
        return Response(output_serializer, status=status.HTTP_200_OK)
