from rest_framework import serializers
from api.models import AccessType, AccessObject, AccessTypeTemplate


class AccessTypeModelSerializer(serializers.ModelSerializer):
    """Сериализатор вывода информации о типе доступа"""

    object_name = serializers.CharField(
        source='object.name',
        read_only=True
    )
    template_name = serializers.CharField(
        source='template.name',
        read_only=True
    )
    node_name = serializers.CharField(
        source='object.node.name',
        read_only=True
    )
    section_name = serializers.CharField(
        source='object.node.section.name',
        read_only=True
    )
    registry_name = serializers.CharField(
        source='object.node.section.registry.name',
        read_only=True
    )

    class Meta:
        model = AccessType
        fields = [
            'id', 'object', 'object_name', 'template', 'template_name',
            'node_name', 'section_name', 'registry_name'
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request = self.context.get('request')

        if request and request.user.is_staff:
            representation['is_deleted'] = instance.is_deleted
        return representation


class AccessTypeCreateInputSerializer(serializers.Serializer):
    """Сериализатор создания типа доступа"""

    object_id = serializers.IntegerField(
        help_text="ID объекта доступа"
    )
    template_id = serializers.IntegerField(
        help_text="ID шаблона типа доступа"
    )

    def validate_object_id(self, value):
        if not AccessObject.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError(
                "Объект доступа не найден или удалён")
        return value

    def validate_template_id(self, value):
        if not AccessTypeTemplate.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError(
                "Шаблон типа доступа не найден или удалён")
        return value

    def validate(self, data):
        if AccessType.objects.filter(
            object_id=data['object_id'],
            template_id=data['template_id'],
            is_deleted=False
        ).exists():
            raise serializers.ValidationError(
                "Тип доступа для данного объекта и шаблона уже существует"
            )
        return data


class AccessTypeCreateOutputSerializer(serializers.Serializer):
    """Сериализатор создания типа доступа"""
    id = serializers.IntegerField()
    object_id = serializers.IntegerField()
    template_id = serializers.IntegerField()
