from django_filters import rest_framework as filters
from api.models import AccessType


class AccessTypeFilter(filters.FilterSet):
    """Фильтры для типов доступа"""

    id = filters.NumberFilter(
        field_name='id'
    )

    object_id = filters.NumberFilter(
        field_name='object__id'
    )
    object_name = filters.CharFilter(
        field_name='object__name',
        lookup_expr='icontains'
    )
    node_id = filters.NumberFilter(
        field_name='object__node__id'
    )
    section_id = filters.NumberFilter(
        field_name='object__node__section__id'
    )
    registry_id = filters.NumberFilter(
        field_name='object__node__section__registry__id'
    )

    template_id = filters.NumberFilter(
        field_name='template__id'
    )
    template_name = filters.CharFilter(
        field_name='template__name',
        lookup_expr='icontains'
    )

    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('object__name', 'object_name'),
            ('template__name', 'template_name'),
        ),
        field_labels={
            'id': 'ID',
            'object__name': 'Объект доступа',
            'template__name': 'Шаблон типа доступа',
        }
    )
