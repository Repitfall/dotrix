from rest_framework import serializers

from api.models import AccessRegistry, AccessGroup


class AccessRegistryModelSerializer(serializers.ModelSerializer):
    """Сериализатор вывода информации о реестре доступа"""

    class Meta:
        model = AccessRegistry
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request = self.context.get('request')

        if request and request.user.is_staff:
            representation['is_deleted'] = instance.is_deleted

        return representation

    def validate_name(self, value):
        instance_id = self.instance.id if hasattr(self, 'instance') else None
        if AccessRegistry.objects.exclude(id=instance_id).filter(name=value).exists():
            raise serializers.ValidationError(
                "Реестр с таким названием уже существует")
        return value


class AccessRegistryCreateInputSerializer(serializers.Serializer):
    """Сериализатор создания реестра доступа"""

    name = serializers.CharField(
        help_text="Название реестра",
        max_length=64
    )
    description = serializers.CharField(
        help_text="Описание реестра",
        required=False,
        allow_blank=True
    )
    owner_group_ids = serializers.ListField(
        help_text="ID групп руководителей",
        child=serializers.IntegerField(),
        required=False,
        default=list
    )

    def validate_name(self, value):
        instance_id = self.instance.id if hasattr(self, 'instance') else None
        if AccessRegistry.objects.exclude(id=instance_id).filter(name=value).exists():
            raise serializers.ValidationError(
                "Реестр с таким названием уже существует")
        return value

    def validate_owner_group_ids(self, value):
        if value:
            existing_groups = AccessGroup.objects.filter(
                id__in=value,
                is_deleted=False
            )
            if len(existing_groups) != len(value):
                raise serializers.ValidationError(
                    "Некоторые группы не найдены"
                )
        return value


class AccessRegistryCreateOutputSerializer(serializers.Serializer):
    """Сериализатор создания реестра доступа"""

    id = serializers.IntegerField()
    name = serializers.CharField(
        help_text="Название реестра",
        max_length=64
    )
    description = serializers.CharField(
        help_text="Описание реестра"
    )
    owner_group_ids = serializers.ListField(
        help_text="ID групп руководителей",
        child=serializers.IntegerField(),
        default=list
    )


class AccessRegistryUpdateInputSerializer(serializers.Serializer):
    """Сериализатор обновления реестра доступа"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = self.context.get('instance') if self.context else None

    name = serializers.CharField(
        help_text="Название реестра",
        max_length=64,
        required=False
    )
    description = serializers.CharField(
        help_text="Описание реестра",
        required=False,
        allow_blank=True
    )
    owner_group_ids = serializers.ListField(
        help_text="ID групп руководителей",
        child=serializers.IntegerField(),
        required=False,
        default=list
    )

    def validate_name(self, value):
        instance_id = self.instance.id if hasattr(self, 'instance') else None
        if AccessRegistry.objects.exclude(id=instance_id).filter(name=value).exists():
            raise serializers.ValidationError(
                "Реестр с таким названием уже существует")
        return value

    def validate_owner_group_ids(self, value):
        if value:
            existing_groups = AccessGroup.objects.filter(
                id__in=value,
                is_deleted=False
            )
            if len(existing_groups) != len(value):
                raise serializers.ValidationError(
                    "Некоторые группы не найдены"
                )
        return value


class AccessRegistryFullUpdateInputSerializer(serializers.Serializer):
    """Сериализатор обновления реестра доступа"""

    name = serializers.CharField(
        help_text="Название реестра",
        max_length=64,
        required=True
    )
    description = serializers.CharField(
        help_text="Описание реестра",
        required=False,
        allow_blank=True
    )
    owner_group_ids = serializers.ListField(
        help_text="ID групп руководителей",
        child=serializers.IntegerField(),
        required=False,
        default=list
    )

    def validate_name(self, value):
        instance_id = self.instance.id if hasattr(self, 'instance') else None
        if AccessRegistry.objects.exclude(id=instance_id).filter(name=value).exists():
            raise serializers.ValidationError(
                "Реестр с таким названием уже существует")
        return value

    def validate_owner_group_ids(self, value):
        if value:
            existing_groups = AccessGroup.objects.filter(
                id__in=value,
                is_deleted=False
            )
            if len(existing_groups) != len(value):
                raise serializers.ValidationError(
                    "Некоторые группы не найдены"
                )
        return value
