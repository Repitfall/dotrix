from django_filters import rest_framework as filters
from api.models import AccessSection


class AccessSectionFilter(filters.FilterSet):
    """Фильтры для разделов доступа"""

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

    registry_id = filters.NumberFilter(
        field_name='registry__id'
    )
    registry_name = filters.CharFilter(
        field_name='registry__name',
        lookup_expr='icontains'
    )
    is_deleted = filters.BooleanFilter(
        field_name='is_deleted'
    )

    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
            ('registry__name', 'registry_name'),
        ),
        field_labels={
            'id': 'ID',
            'name': 'Название',
            'registry__name': 'Реестр',
        }
    )
