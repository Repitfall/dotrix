from rest_framework import serializers

from api.models import AuditEntry


class AuditModelSerializer(serializers.ModelSerializer):
    """Сериализатор вывода информации о записи аудита"""

    user_name = serializers.SerializerMethodField(
        help_text="Имя пользователя"
    )
    content_type_model = serializers.CharField(
        help_text="Тип модели",
        source='content_type.model',
        read_only=True)
    registry_name = serializers.CharField(
        help_text="Название реестра",
        source='registry.name',
        read_only=True
    )

    class Meta:
        model = AuditEntry
        fields = [
            'id', 'user', 'user_name', 'action', 'content_type_model',
            'object_id', 'object_repr', 'changes', 'timestamp',
            'registry', 'registry_name'
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name()
        return None
