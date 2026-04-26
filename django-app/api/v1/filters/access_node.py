from django_filters import rest_framework as filters
from api.models import AccessNode


class AccessNodeFilter(filters.FilterSet):
    """Фильтры для узлов доступа"""

    id = filters.NumberFilter(
        field_name='id'
    )
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='exact'
    )
    name_contains = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    section_id = filters.NumberFilter(
        field_name='section__id'
    )
    section_name = filters.CharFilter(
        field_name='section__name',
        lookup_expr='icontains'
    )

    registry_id = filters.NumberFilter(
        field_name='section__registry__id'
    )

    ip = filters.CharFilter(
        field_name='ip',
        lookup_expr='exact'
    )
    ip_contains = filters.CharFilter(
        field_name='ip',
        lookup_expr='icontains'
    )

    has_ip = filters.BooleanFilter(
        field_name='ip',
        lookup_expr='isnull',
        method='filter_has_ip'
    )

    ip_validated = filters.BooleanFilter(
        field_name='ip_validated'
    )
    has_validation_error = filters.BooleanFilter(
        method='filter_has_error'
    )

    is_deleted = filters.BooleanFilter(
        field_name='is_deleted'
    )

    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
            ('section__name', 'section_name'),
            ('ip', 'ip'),
            ('ip_validated', 'ip_validated'),
        ),
        field_labels={
            'id': 'ID',
            'name': 'Название',
            'section__name': 'Раздел',
            'ip': 'IP-адрес',
            'ip_validated': 'IP валидирован',
        }
    )

    def filter_has_ip(self, queryset, name, value):
        """Фильтр по наличию IP-адреса"""
        if value:
            return queryset.filter(ip__isnull=False)
        return queryset.filter(ip__isnull=True)

    def filter_has_error(self, queryset, name, value):
        """Фильтр по наличию ошибки валидации"""
        if value:
            return queryset.filter(last_validation_error__isnull=False, last_validation_error__gt='')
        return queryset.filter(last_validation_error__isnull=True)
