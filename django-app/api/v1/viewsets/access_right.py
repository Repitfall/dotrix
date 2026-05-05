from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.models import AccessRight, AccessRegistry, AccessGroup
from api.v1.permissions import IsAdmin, CanManageGroup
from api.v1.serializers.access_right import (
    AccessRightModelSerializer,
    AccessRightCreateInputSerializer,
    AccessRightCreateOutputSerializer,
    AccessRightUpdateInputSerializer,
)
from api.v1.serializers.error import ErrorOutputSerializer
from api.v1.services.access_right import AccessRightService
from api.v1.services.pagination import Pagination
from api.v1.filters.access_right import AccessRightFilter


class AccessRightViewSet(viewsets.GenericViewSet):
    """Управление назначениями прав группам"""

    pagination_class = Pagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AccessRightFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AccessRight.objects.all()
        else:
            user_groups = user.access_groups.filter(is_deleted=False)
            registry_ids = AccessRegistry.objects.filter(
                groups__in=user_groups,
                is_deleted=False
            ).values_list('id', flat=True).distinct()

            return AccessRight.objects.filter(
                access_type__object__node__section__registry_id__in=registry_ids
            )

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    @extend_schema(
        summary="Список назначений прав",
        responses={
            200: AccessRightModelSerializer,
            401: ErrorOutputSerializer
        },
        tags=['Права доступа']
    )
    def list(self, request):
        page = self.paginate_queryset(
            self.filter_queryset(self.get_queryset()))
        output_serializer = AccessRightModelSerializer(
            page, many=True, context=self.get_serializer_context()).data
        return self.get_paginated_response(output_serializer)

    @extend_schema(
        summary="Просмотр назначения права",
        responses={
            200: AccessRightModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Права доступа']
    )
    def retrieve(self, request, pk=None):
        access_right = get_object_or_404(self.get_queryset(), id=pk)
        output_serializer = AccessRightModelSerializer(
            access_right, context=self.get_serializer_context()).data
        return Response(output_serializer)

    @extend_schema(
        summary="Назначить право группе",
        request=AccessRightCreateInputSerializer,
        responses={
            201: AccessRightCreateOutputSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer
        },
        tags=['Права доступа']
    )
    def create(self, request):
        input_serializer = AccessRightCreateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(ErrorOutputSerializer({
                'error': "Некорректные данные",
                'detail': input_serializer.errors
            }).data, status=status.HTTP_400_BAD_REQUEST)

        access_right, error = AccessRightService.create_access_right(
            input_serializer.validated_data,
            granted_by=request.user
        )
        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка назначения",
                    'detail': error
                }).data, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = AccessRightCreateOutputSerializer({
            'id': access_right.id,
            'access_type_id': access_right.access_type_id,
            'group_id': access_right.group_id,
            'granted_at': access_right.granted_at,
            'expires_at': access_right.expires_at
        })
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Частичное обновление права",
        request=AccessRightUpdateInputSerializer,
        responses={
            200: AccessRightModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Права доступа']
    )
    def partial_update(self, request, pk=None):
        access_right = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, access_right)

        input_serializer = AccessRightUpdateInputSerializer(
            data=request.data, partial=True)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors}).data,
                status=status.HTTP_400_BAD_REQUEST)

        updated, error = AccessRightService.update_access_right(
            access_right, input_serializer.validated_data, request.user)
        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error}).data,
                status=status.HTTP_400_BAD_REQUEST)

        output_serializer = AccessRightModelSerializer(
            updated, context=self.get_serializer_context()).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Отозвать право",
        responses={
            204: OpenApiResponse(description="Право отозвано"),
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Права доступа']
    )
    def destroy(self, request, pk=None):
        access_right = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, access_right)

        ticket = request.data.get('ticket')
        success, error = AccessRightService.delete_access_right(
            access_right, request.user, ticket)
        if error:
            return Response(ErrorOutputSerializer({
                'error': "Ошибка отзыва",
                'detail': error}).data,
                status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
