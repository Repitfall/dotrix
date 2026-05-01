from django_filters import rest_framework as filters
from api.models import AccessRight


class AccessRightFilter(filters.FilterSet):
    """Фильтры для назначений прав группам"""

    id = filters.NumberFilter(
        field_name='id'
    )
    access_type_id = filters.NumberFilter(
        field_name='access_type__id'
    )
    group_id = filters.NumberFilter(
        field_name='group__id'
    )
    granted_by_id = filters.NumberFilter(
        field_name='granted_by__id'
    )

    granted_at_after = filters.DateTimeFilter(
        field_name='granted_at',
        lookup_expr='gte'
    )
    granted_at_before = filters.DateTimeFilter(
        field_name='granted_at',
        lookup_expr='lte'
    )

    expires_at_after = filters.DateTimeFilter(
        field_name='expires_at',
        lookup_expr='gte'
    )
    expires_at_before = filters.DateTimeFilter(
        field_name='expires_at',
        lookup_expr='lte'
    )
    has_expired = filters.BooleanFilter(
        method='filter_has_expired'
    )

    object_id = filters.NumberFilter(
        field_name='access_type__object__id'
    )
    node_id = filters.NumberFilter(
        field_name='access_type__object__node__id'
    )
    section_id = filters.NumberFilter(
        field_name='access_type__object__node__section__id'
    )
    registry_id = filters.NumberFilter(
        field_name='access_type__object__node__section__registry__id'
    )

    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('granted_at', 'granted_at'),
            ('expires_at', 'expires_at'),
            ('access_type__object__name', 'object_name'),
            ('group__name', 'group_name'),
        ),
        field_labels={
            'id': 'ID',
            'granted_at': 'Дата назначения',
            'expires_at': 'Дата истечения',
            'access_type__object__name': 'Объект доступа',
            'group__name': 'Группа',
        }
    )

    def filter_has_expired(self, queryset, name, value):
        """Фильтр по истечению срока действия"""
        from django.utils import timezone
        now = timezone.now()
        if value:
            return queryset.filter(expires_at__lte=now)
        return queryset.filter(expires_at__isnull=True) | queryset.filter(expires_at__gt=now)
