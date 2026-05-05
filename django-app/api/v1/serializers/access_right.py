from rest_framework import serializers
from api.models import AccessRight, AccessType, AccessGroup, User
from django.utils import timezone


class AccessRightModelSerializer(serializers.ModelSerializer):
    """Сериализатор вывода информации о назначении права"""

    access_type_object_name = serializers.CharField(
        source='access_type.object.name',
        read_only=True
    )
    access_type_template_name = serializers.CharField(
        source='access_type.template.name',
        read_only=True
    )
    group_name = serializers.CharField(
        source='group.name',
        read_only=True
    )
    granted_by_username = serializers.CharField(
        source='granted_by.username',
        read_only=True
    )
    registry_name = serializers.CharField(
        source='access_type.object.node.section.registry.name',
        read_only=True
    )
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = AccessRight
        fields = [
            'id', 'access_type', 'access_type_object_name', 'access_type_template_name',
            'group', 'group_name', 'granted_at', 'granted_by', 'granted_by_username',
            'expires_at', 'registry_name', 'is_active', 'ticket'
        ]
        read_only_fields = ['id', 'granted_at', 'granted_by']

    def get_is_active(self, obj):
        """Активно ли право (не истекло)"""
        if obj.expires_at:
            return obj.expires_at > timezone.now()
        return True


class AccessRightCreateInputSerializer(serializers.Serializer):
    """Сериализатор создания назначения права"""

    access_type_id = serializers.IntegerField(
        help_text="ID типа доступа"
    )
    group_id = serializers.IntegerField(
        help_text="ID группы доступа"
    )
    expires_at = serializers.DateTimeField(
        help_text="Срок действия",
        required=False,
        allow_null=True
    )
    ticket = serializers.CharField(
        max_length=9,
        required=False,
        allow_null=True,
        help_text="Номер тикета"
    )

    def validate_access_type_id(self, value):
        if not AccessType.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Тип доступа не найден или удалён")
        return value

    def validate_group_id(self, value):
        if not AccessGroup.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError("Группа не найдена или удалена")
        return value

    def validate(self, data):
        if AccessRight.objects.filter(
            access_type_id=data['access_type_id'],
            group_id=data['group_id']
        ).exists():
            raise serializers.ValidationError(
                "Данное право уже назначено этой группе")

        access_type = AccessType.objects.select_related(
            'object__node__section__registry').get(id=data['access_type_id'])
        group = AccessGroup.objects.select_related(
            'registry').get(id=data['group_id'])
        if access_type.object.node.section.registry_id != group.registry_id:
            raise serializers.ValidationError(
                "Группа и тип доступа должны находиться в одном реестре")

        return data


class AccessRightCreateOutputSerializer(serializers.Serializer):
    """Сериализатор создания назначения права"""
    id = serializers.IntegerField()
    access_type_id = serializers.IntegerField()
    group_id = serializers.IntegerField()
    granted_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField(
        allow_null=True
    )


class AccessRightUpdateInputSerializer(serializers.Serializer):
    """Сериализатор продления назначения права"""
    expires_at = serializers.DateTimeField(
        help_text="Новый срок действия",
        required=False,
        allow_null=True
    )
