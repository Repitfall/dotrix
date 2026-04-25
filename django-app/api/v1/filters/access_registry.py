from api.models import AccessRegistry
from django_filters import rest_framework as filters


class AccessRegistryFilter(filters.FilterSet):
    """Фильтры для реестров доступа"""

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
    description_contains = filters.CharFilter(
        field_name='description',
        lookup_expr='icontains'
    )

    is_deleted = filters.BooleanFilter(
        field_name='is_deleted'
    )

    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
        ),
        field_labels={
            'id': 'ID',
            'name': 'Название',
        }
    )
