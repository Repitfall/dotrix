from rest_framework import serializers
from api.models import AccessObject, AccessNode, AccessType


class AccessObjectModelSerializer(serializers.ModelSerializer):
    """Сериализатор вывода информации об объекте доступа"""

    node_name = serializers.CharField(
        source='node.name',
        read_only=True
    )
    section_name = serializers.CharField(
        source='node.section.name',
        read_only=True
    )
    registry_name = serializers.CharField(
        source='node.section.registry.name',
        read_only=True
    )
    count_types = serializers.SerializerMethodField()

    class Meta:
        model = AccessObject
        fields = [
            'id', 'name', 'description', 'resource_path', 'node', 'node_name',
            'section_name', 'registry_name', 'count_types'
        ]
        read_only_fields = ['id']

    def get_count_types(self, obj):
        """Количество активных типов доступа у объекта"""
        return obj.types.filter(is_deleted=False).count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.user.is_staff:
            representation['is_deleted'] = instance.is_deleted

        return representation


class AccessObjectCreateInputSerializer(serializers.Serializer):
    """Сериализатор создания объекта доступа"""

    name = serializers.CharField(
        help_text="Название объекта",
        max_length=64
    )
    description = serializers.CharField(
        help_text="Описание",
        required=False,
        allow_blank=True
    )
    resource_path = serializers.CharField(
        help_text="Путь к ресурсу",
        max_length=256
    )
    node_id = serializers.IntegerField(
        help_text="ID узла доступа"
    )

    def validate_node_id(self, value):
        """Проверка существования узла"""
        if not AccessNode.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError("Узел не найден")
        return value

    def validate_name(self, value):
        """Проверка уникальности имени в рамках узла"""
        node_id = self.initial_data.get('node_id')
        if node_id:
            if AccessObject.objects.filter(
                node_id=node_id,
                name=value,
                is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    "Объект с таким именем уже существует на этом узле"
                )
        return value

    def validate_resource_path(self, value):
        """resource_path не может быть пустым"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Путь к ресурсу не может быть пустым")
        return value


class AccessObjectCreateOutputSerializer(serializers.Serializer):
    """Сериализатор создания объекта доступа"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    resource_path = serializers.CharField()
    node_id = serializers.IntegerField()


class AccessObjectUpdateInputSerializer(serializers.Serializer):
    """Сериализатор обновления объекта доступа"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = self.context.get('instance') if self.context else None

    name = serializers.CharField(
        help_text="Название объекта",
        max_length=64,
        required=False
    )
    description = serializers.CharField(
        help_text="Описание",
        required=False,
        allow_blank=True
    )
    resource_path = serializers.CharField(
        help_text="Путь к ресурсу",
        max_length=256,
        required=False
    )

    def validate_name(self, value):
        if value and self.instance:
            if AccessObject.objects.exclude(id=self.instance.id).filter(
                node=self.instance.node,
                name=value,
                is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    "Объект с таким именем уже существует на этом узле"
                )
        return value

    def validate_resource_path(self, value):
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError(
                "Путь к ресурсу не может быть пустым")
        return value
