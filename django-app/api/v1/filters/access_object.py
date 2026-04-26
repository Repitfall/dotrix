from django_filters import rest_framework as filters
from api.models import AccessObject


class AccessObjectFilter(filters.FilterSet):
    """Фильтры для объектов доступа"""

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

    node_id = filters.NumberFilter(
        field_name='node__id'
    )
    node_name = filters.CharFilter(
        field_name='node__name',
        lookup_expr='icontains'
    )

    section_id = filters.NumberFilter(
        field_name='node__section__id'
    )
    registry_id = filters.NumberFilter(
        field_name='node__section__registry__id'
    )

    resource_path = filters.CharFilter(
        field_name='resource_path',
        lookup_expr='icontains'
    )
    resource_path_exact = filters.CharFilter(
        field_name='resource_path',
        lookup_expr='exact'
    )

    is_deleted = filters.BooleanFilter(
        field_name='is_deleted'
    )

    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
            ('node__name', 'node_name'),
            ('resource_path', 'resource_path'),
        ),
        field_labels={
            'id': 'ID',
            'name': 'Название',
            'node__name': 'Узел',
            'resource_path': 'Путь к ресурсу',
        }
    )
