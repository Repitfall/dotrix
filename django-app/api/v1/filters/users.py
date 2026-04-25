from django_filters import rest_framework as filters
from api.models import User


class UserFilter(filters.FilterSet):
    """Фильтры для пользователей"""

    id = filters.NumberFilter(
        field_name='id'
    )

    login = filters.CharFilter(
        field_name='username',
        lookup_expr='exact'
    )
    login_contains = filters.CharFilter(
        field_name='username',
        lookup_expr='icontains'
    )

    last_name = filters.CharFilter(
        field_name='last_name',
        lookup_expr='icontains'
    )
    first_name = filters.CharFilter(
        field_name='first_name',
        lookup_expr='icontains'
    )
    patronymic = filters.CharFilter(
        field_name='patronymic',
        lookup_expr='icontains'
    )
    post = filters.CharFilter(
        field_name='post',
        lookup_expr='icontains'
    )

    is_active = filters.BooleanFilter(
        field_name='is_active'
    )
    is_deleted = filters.BooleanFilter(
        field_name='is_deleted'
    )
    reset_password = filters.BooleanFilter(
        field_name='reset_password'
    )

    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    created_at = filters.DateTimeFromToRangeFilter(
        field_name='created_at'
    )

    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('username', 'login'),
            ('last_name', 'last_name'),
            ('first_name', 'first_name'),
            ('created_at', 'created_at'),
            ('is_active', 'is_active'),
        ),
        field_labels={
            'id': 'ID',
            'username': 'Логин',
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'created_at': 'Дата создания',
            'is_active': 'Активация аккаунта',
        }
    )
