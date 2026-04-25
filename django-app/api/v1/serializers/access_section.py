from rest_framework import serializers

from api.models import AccessSection, AccessRegistry


class AccessSectionModelSerializer(serializers.ModelSerializer):
    """Сериализатор вывода информации о группе доступа"""

    registry_name = serializers.CharField(
        source='registry.name',
        read_only=True)

    class Meta:
        model = AccessSection
        fields = ['id', 'name', 'description', 'registry', 'registry_name']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.user.is_staff:
            representation['is_deleted'] = instance.is_deleted

        return representation


class AccessSectionCreateInputSerializer(serializers.Serializer):
    """Сериализатор создания раздела доступа"""

    name = serializers.CharField(
        help_text="Название группы",
        max_length=64
    )
    description = serializers.CharField(
        help_text="Описание",
        required=False,
        allow_blank=True
    )
    registry_id = serializers.IntegerField(
        help_text="ID реестра доступа"
    )

    def validate_registry_id(self, value):
        if not AccessRegistry.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError("Реестр не найден")
        return value

    def validate_name(self, value):
        """Проверка уникальности имени в рамках реестра"""
        registry_id = self.initial_data.get('registry_id')
        if registry_id:
            if AccessSection.objects.filter(
                registry_id=registry_id,
                name=value,
                is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    "Раздел с таким именем уже существует в этом реестре"
                )
        return value


class AccessSectionCreateOutputSerializer(serializers.Serializer):
    """Сериализатор создания раздела доступа"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    registry_id = serializers.IntegerField()


class AccessSectionUpdateInputSerializer(serializers.Serializer):
    """Сериализатор обновления раздела доступа"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = self.context.get('instance') if self.context else None

    name = serializers.CharField(
        help_text="Название раздела", max_length=64, required=False)
    description = serializers.CharField(
        help_text="Описание", required=False, allow_blank=True)

    def validate_name(self, value):
        """Проверка уникальности имени в рамках реестра"""
        if value and self.instance:
            if AccessSection.objects.exclude(id=self.instance.id).filter(
                registry=self.instance.registry,
                name=value,
                is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    "Раздел с таким именем уже существует в этом реестре"
                )
        return value
