from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from api.v1.serializers.error import ErrorOutputSerializer
from api.v1.serializers.audit import AuditModelSerializer
from api.models import AuditEntry, AccessRegistry
from api.v1.filters.audit import AuditFilter
from api.v1.services.pagination import Pagination


class AuditViewSet(viewsets.GenericViewSet):
    """Просмотр журнала аудита"""

    pagination_class = Pagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AuditFilter
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Начальный список для работы"""
        user = self.request.user

        if user.is_staff:
            return AuditEntry.objects.all()
        else:
            owned_registry_ids = AccessRegistry.objects.filter(
                owner_groups__in=user.access_groups.filter(is_deleted=False),
                is_deleted=False
            ).values_list('id', flat=True).distinct()

            return AuditEntry.objects.filter(registry_id__in=owned_registry_ids)

    @extend_schema(
        summary="Список записей аудита",
        description="Возвращает список всех записей аудита (с учетом прав)",
        responses={
            200: AuditModelSerializer,
            401: ErrorOutputSerializer,
        },
        tags=['Журнал аудита']
    )
    def list(self, request):
        page = self.paginate_queryset(
            self.filter_queryset(
                self.get_queryset()))
        output_serializer = AuditModelSerializer(
            page,
            many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(output_serializer.data)

    @extend_schema(
        summary="Просмотр записи аудита",
        description="Возвращает информацию о конкретной записи аудита",
        responses={
            200: AuditModelSerializer,
            401: ErrorOutputSerializer,
            403: ErrorOutputSerializer,
            404: ErrorOutputSerializer
        },
        tags=['Журнал аудита']
    )
    def retrieve(self, request, pk=None):
        entry = get_object_or_404(self.get_queryset(), id=pk)
        self.check_object_permissions(request, entry)
        output_serializer = AuditModelSerializer(entry)
        return Response(output_serializer.data)
