from django_filters import rest_framework as filters
from api.models import AuditEntry


class AuditFilter(filters.FilterSet):
    action = filters.ChoiceFilter(
        choices=AuditEntry.action.field.choices
    )
    user_id = filters.NumberFilter(
        field_name='user_id'
    )
    registry_id = filters.NumberFilter(
        field_name='registry_id'
    )
    timestamp_after = filters.DateTimeFilter(
        field_name='timestamp',
        lookup_expr='gte'
    )
    timestamp_before = filters.DateTimeFilter(
        field_name='timestamp',
        lookup_expr='lte'
    )
    content_type_model = filters.CharFilter(
        field_name='content_type__model'
    )

    ordering = filters.OrderingFilter(
        fields=(
            ('timestamp', 'timestamp'),
            ('user__username', 'user'),
            ('registry__name', 'registry_name'),
        ),
        field_labels={
            'timestamp': 'Дата события',
            'user__username': 'Пользователь',
            'registry__name': 'Реестр',
        }
    )
