from django_filters import rest_framework as filters
from api.models import AccessTypeTemplate


class AccessTypeTemplateFilter(filters.FilterSet):
    """Фильтры для шаблонов типов доступа"""

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

    class Meta:
        model = AccessTypeTemplate
        fields = ['id', 'name', 'is_deleted']
