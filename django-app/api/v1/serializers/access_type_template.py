from rest_framework import serializers
from api.models import AccessTypeTemplate


class AccessTypeTemplateModelSerializer(serializers.ModelSerializer):
    """Сериализатор вывода информации о шаблоне типа доступа"""

    class Meta:
        model = AccessTypeTemplate
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_staff:
            representation['is_deleted'] = instance.is_deleted
        return representation


class AccessTypeTemplateCreateInputSerializer(serializers.Serializer):
    """Сериализатор создания шаблона типа доступа"""

    name = serializers.CharField(
        help_text="Название шаблона",
        max_length=64
    )
    description = serializers.CharField(
        help_text="Описание",
        required=False,
        allow_blank=True
    )

    def validate_name(self, value):
        if AccessTypeTemplate.objects.filter(name=value, is_deleted=False).exists():
            raise serializers.ValidationError(
                "Шаблон с таким названием уже существует")
        return value


class AccessTypeTemplateCreateOutputSerializer(serializers.Serializer):
    """Сериализатор создания шаблона типа доступа"""
    id = serializers.IntegerField()
    name = serializers.CharField(
        help_text="Название шаблона",
        max_length=64
    )
    description = serializers.CharField(
        allow_blank=True
    )


class AccessTypeTemplateUpdateInputSerializer(serializers.Serializer):
    """Сериализатор обновления шаблона типа доступа"""

    name = serializers.CharField(
        help_text="Название шаблона",
        max_length=64,
        required=False,
    )
    description = serializers.CharField(
        required=False, allow_blank=True, help_text="Описание")

    def validate_name(self, value):
        if value and self.instance:
            if AccessTypeTemplate.objects.exclude(id=self.instance.id).filter(
                    name=value, is_deleted=False).exists():
                raise serializers.ValidationError(
                    "Шаблон с таким названием уже существует")
        return value
