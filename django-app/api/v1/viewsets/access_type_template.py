from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.models import AccessTypeTemplate
from api.v1.permissions import IsAdmin, IsAdminOrReadOnly
from api.v1.serializers.access_type_template import (
    AccessTypeTemplateModelSerializer,
    AccessTypeTemplateCreateInputSerializer,
    AccessTypeTemplateCreateOutputSerializer,
    AccessTypeTemplateUpdateInputSerializer
)
from api.v1.serializers.error import ErrorOutputSerializer
from api.v1.services.access_type_template import AccessTypeTemplateService
from api.v1.services.pagination import Pagination
from api.v1.filters.access_type_template import AccessTypeTemplateFilter


class AccessTypeTemplateViewSet(viewsets.GenericViewSet):
    """Управление шаблонами типов доступа"""

    pagination_class = Pagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AccessTypeTemplateFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AccessTypeTemplate.objects.all()
        return AccessTypeTemplate.objects.filter(is_deleted=False)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'restore']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsAdminOrReadOnly()]

    @extend_schema(
        summary="Список шаблонов типов доступа",
        description="Возвращает список всех доступных шаблонов типов доступа (с учетом прав)",
        responses={
            200: AccessTypeTemplateModelSerializer,
            401: ErrorOutputSerializer
        },
        tags=['Шаблоны типов доступа']
    )
    def list(self, request):
        page = self.paginate_queryset(
            self.filter_queryset(self.get_queryset()))
        serializer = AccessTypeTemplateModelSerializer(
            page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Просмотр шаблона типа доступа",
        description="Возвращает информацию о конкретном шаблоне типа доступа",
        responses={
            200: AccessTypeTemplateModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Шаблоны типов доступа']
    )
    def retrieve(self, request, pk=None):
        template = get_object_or_404(self.get_queryset(), id=pk)
        output_serializer = AccessTypeTemplateModelSerializer(
            template, context=self.get_serializer_context()).data
        return Response(output_serializer)

    @extend_schema(
        summary="Создание шаблона типа доступа",
        request=AccessTypeTemplateCreateInputSerializer,
        responses={
            201: AccessTypeTemplateCreateOutputSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer
        },
        tags=['Шаблоны типов доступа']
    )
    def create(self, request):
        input_serializer = AccessTypeTemplateCreateInputSerializer(
            data=request.data)
        if not input_serializer.is_valid():
            return Response(
                ErrorOutputSerializer({
                    'error': "Некорректные данные",
                    'detail': input_serializer.errors
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        template, error = AccessTypeTemplateService.create_template(
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

        output_serializer = AccessTypeTemplateCreateOutputSerializer({
            'id': template.id,
            'name': template.name,
            'description': template.description
        }).data
        return Response(output_serializer, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Обновление шаблона типа доступа",
        description="Обновляет часть данных шаблонов типа доступа",
        request=AccessTypeTemplateUpdateInputSerializer,
        responses={
            200: AccessTypeTemplateModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Шаблоны типов доступа']
    )
    def partial_update(self, request, pk=None):
        template = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, template)

        input_serializer = AccessTypeTemplateUpdateInputSerializer(
            instance=template,
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

        updated, error = AccessTypeTemplateService.update_template(
            template, input_serializer.validated_data, request.user
        )
        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessTypeTemplateModelSerializer(
            updated).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Полное обновление шаблона",
        description="Обновляет все данные шаблона типов доступа",
        request=AccessTypeTemplateUpdateInputSerializer,
        responses={
            200: AccessTypeTemplateModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Шаблоны типов доступа']
    )
    def update(self, request, pk=None):
        template = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, template)

        input_serializer = AccessTypeTemplateUpdateInputSerializer(
            instance=template,
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

        updated, error = AccessTypeTemplateService.update_template(
            template, input_serializer.validated_data, request.user)
        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка обновления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        output_serializer = AccessTypeTemplateModelSerializer(updated).data
        return Response(output_serializer, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Удаление шаблона типа доступа",
        description="Помечает шаблон типа доступа как удаленный",
        responses={
            204: OpenApiResponse(description="Успешное удаление"),
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Шаблоны типов доступа']
    )
    def destroy(self, request, pk=None):
        template = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, template)

        success, error = AccessTypeTemplateService.delete_template(
            template, request.user)

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
        summary="Восстановление шаблона",
        description="Восстанавливает удаленный шаблон типа доступа",
        responses={
            200: AccessTypeTemplateModelSerializer,
            400: ErrorOutputSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Шаблоны типов доступа']
    )
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        template = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, template)

        success, error = AccessTypeTemplateService.restore_template(
            template, request.user)

        if error:
            return Response(
                ErrorOutputSerializer({
                    'error': "Ошибка восстановления",
                    'detail': error
                }).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        output_serializer = AccessTypeTemplateModelSerializer(
            template, context=self.get_serializer_context()).data
        return Response(output_serializer, status=status.HTTP_200_OK)
