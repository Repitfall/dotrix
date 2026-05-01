from rest_framework import serializers

from api.models import AccessGroup, AccessRegistry, User


class AccessGroupModelSerializer(serializers.ModelSerializer):
    """Сериализатор вывода информации о группе доступа"""

    registry_name = serializers.CharField(
        source='registry.name',
        read_only=True)
    parent_group_name = serializers.CharField(
        source='parent_group.name',
        read_only=True)
    user_count = serializers.SerializerMethodField()
    owner_of_registries = serializers.SerializerMethodField()

    class Meta:
        model = AccessGroup
        fields = [
            'id', 'name', 'description', 'registry', 'registry_name',
            'parent_group', 'parent_group_name', 'user_count',
            'owner_of_registries'
        ]
        read_only_fields = ['id']

    def get_user_count(self, obj):
        return len(obj.get_all_users())

    def get_owner_of_registries(self, obj):
        return list(obj.owned_registries.values_list('id', flat=True))

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.user.is_staff:
            representation['is_deleted'] = instance.is_deleted

        return representation


class AccessGroupCreateInputSerializer(serializers.Serializer):
    """Сериализатор создания группы доступа"""

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
    parent_group_id = serializers.IntegerField(
        help_text="ID родительской группы",
        required=False,
        allow_null=True
    )
    user_ids = serializers.ListField(
        help_text="ID пользователей в группе",
        child=serializers.IntegerField(),
        required=False,
        default=list
    )
    owner_of_registry_ids = serializers.ListField(
        help_text="ID реестров, где эта группа будет руководителем",
        child=serializers.IntegerField(),
        required=False,
        default=list
    )

    def validate_registry_id(self, value):
        if not AccessRegistry.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError("Реестр не найден")
        return value

    def validate_parent_group_id(self, value):
        try:
            parent = AccessGroup.objects.get(id=value, is_deleted=False)
        except AccessGroup.DoesNotExist:
            raise serializers.ValidationError(
                "Родительская группа не найдена")

        if hasattr(self, 'instance') and self.instance and self.instance.id == value:
            raise serializers.ValidationError(
                "Группа не может быть родителем самой себя")

        if parent.registry.is_deleted:
            raise serializers.ValidationError(
                "Родительская группа находится в удалённом реестре")

        max_depth = 10
        depth = 1
        current = parent
        while current.parent_group:
            depth += 1
            current = current.parent_group
            if depth > max_depth:
                raise serializers.ValidationError(
                    f"Превышена максимальная глубина иерархии ({max_depth} уровней)"
                )

        return value

    def validate_name(self, value):
        registry_id = self.initial_data.get('registry_id')
        if not registry_id and self.instance:
            registry_id = self.instance.registry_id
        instance_id = self.instance.id if hasattr(
            self, 'instance') and self.instance is not None else None
        if AccessGroup.objects.exclude(id=instance_id).filter(
            registry_id=registry_id,
            name=value
        ).exists():
            raise serializers.ValidationError(
                "Группа с таким именем уже существует в этом реестре"
            )
        return value

    def validate_user_ids(self, value):
        if value:
            unique_ids = list(set(value))
            existing_users = User.objects.filter(
                id__in=unique_ids, is_deleted=False)
            if len(existing_users) != len(unique_ids):
                raise serializers.ValidationError(
                    "Некоторые пользователи не найдены")
        return value

    def validate_owner_of_registry_ids(self, value):
        if value:
            existing_registries = AccessRegistry.objects.filter(
                id__in=value,
                is_deleted=False
            )
            if len(existing_registries) != len(set(value)):
                raise serializers.ValidationError(
                    "Некоторые реестры не найдены")
        return value


class AccessGroupCreateOutputSerializer(serializers.Serializer):
    """Сериализатор создания группы доступа"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    registry_id = serializers.IntegerField()
    parent_group_id = serializers.IntegerField(
        allow_null=True
    )
    user_ids = serializers.ListField(
        child=serializers.IntegerField()
    )
    owner_of_registry_ids = serializers.ListField(
        child=serializers.IntegerField()
    )


class AccessGroupUpdateInputSerializer(serializers.Serializer):
    """Сериализатор обновления группы доступа"""

    name = serializers.CharField(
        help_text="Название группы", max_length=64, required=False)
    description = serializers.CharField(
        help_text="Описание", required=False, allow_blank=True)
    parent_group_id = serializers.IntegerField(
        help_text="ID родительской группы", required=False, allow_null=True)
    user_ids = serializers.ListField(
        help_text="ID пользователей в группе",
        child=serializers.IntegerField(),
        required=False
    )
    owner_of_registry_ids = serializers.ListField(
        help_text="ID реестров, где эта группа будет руководителем",
        child=serializers.IntegerField(),
        required=False
    )

    def validate_parent_group_id(self, value):
        if value:
            try:
                parent = AccessGroup.objects.get(id=value, is_deleted=False)

                if hasattr(self, 'instance') and self.instance:
                    if self.instance.id == value:
                        raise serializers.ValidationError(
                            "Группа не может быть родителем самой себя")

                    if self.instance.is_ancestor_of(parent):
                        raise serializers.ValidationError(
                            "Нельзя создать цикл в иерархии групп")

                if hasattr(self, 'instance') and self.instance:
                    if parent.registry_id != self.instance.registry_id:
                        raise serializers.ValidationError(
                            "Родительская группа должна находиться в том же реестре"
                        )

                return value
            except AccessGroup.DoesNotExist:
                raise serializers.ValidationError(
                    "Родительская группа не найдена")
        return value

    def validate_name(self, value):
        registry_id = self.initial_data.get('registry_id')
        if registry_id:
            instance_id = self.instance.id if hasattr(
                self, 'instance') and self.instance is not None else None
            if AccessGroup.objects.exclude(id=instance_id).filter(
                registry_id=registry_id,
                name=value
            ).exists():
                raise serializers.ValidationError(
                    "Группа с таким именем уже существует в этом реестре"
                )
        return value

    def validate_user_ids(self, value):
        if value:
            unique_ids = list(set(value))
            existing_users = User.objects.filter(
                id__in=unique_ids, is_deleted=False)
            if len(existing_users) != len(unique_ids):
                raise serializers.ValidationError(
                    "Некоторые пользователи не найдены")
        return value

    def validate_owner_of_registry_ids(self, value):
        if value:
            existing_registries = AccessRegistry.objects.filter(
                id__in=value,
                is_deleted=False
            )
            if len(existing_registries) != len(set(value)):
                raise serializers.ValidationError(
                    "Некоторые реестры не найдены")
        return value
