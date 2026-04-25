from django_filters import rest_framework as filters
from api.models import AccessGroup


class AccessGroupFilter(filters.FilterSet):
    """Фильтры для групп доступа"""

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

    parent_group_id = filters.NumberFilter(
        field_name='parent_group__id'
    )
    is_deleted = filters.BooleanFilter(
        field_name='is_deleted'
    )

    user_id = filters.NumberFilter(
        field_name='users__id',
        method='filter_by_user'
    )

    owner_for_registry = filters.NumberFilter(
        field_name='owned_registries__id',
        method='filter_by_owner_registry'
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

    def filter_by_user(self, queryset, name, value):
        """Фильтрация групп по пользователю"""
        return queryset.filter(users__id=value)

    def filter_by_owner_registry(self, queryset, name, value):
        """Фильтрация групп, являющихся руководителями конкретного реестра"""
        return queryset.filter(owned_registries__id=value)
