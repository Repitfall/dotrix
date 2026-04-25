from rest_framework import serializers

from api.models import User


class UserModelSerializer(serializers.ModelSerializer):
    """Сериализатор вывода информации о пользователе"""
    login = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ['id', 'login', 'first_name',
                  'last_name', 'patronymic', 'post']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request = self.context.get('request')

        if request and request.user.is_staff:
            representation['is_active'] = instance.is_active
            representation['is_deleted'] = instance.is_deleted

        return representation

    def validate_login(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким логином уже существует")
        return value


class UserCreateInputSerializer(serializers.Serializer):
    """Сериализатор создания пользователя"""

    login = serializers.CharField(
        help_text="Логин пользователя", max_length=64
    )
    last_name = serializers.CharField(
        help_text="Фамилия пользователя", max_length=32, required=False, allow_blank=True
    )
    first_name = serializers.CharField(
        help_text="Имя пользователя", max_length=32, required=False, allow_blank=True
    )
    patronymic = serializers.CharField(
        help_text="Отчество пользователя", max_length=32, required=False, allow_blank=True
    )
    post = serializers.CharField(
        help_text="Должность пользователя", max_length=128, required=False, allow_blank=True
    )
    is_active = serializers.BooleanField(
        help_text="Активация аккаунта", default=True, required=False
    )

    def validate_login(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким логином уже существует")
        return value


class UserCreateOutputSerializer(serializers.Serializer):
    """Сериализатор создания пользователя"""

    id = serializers.IntegerField()
    login = serializers.CharField(
        help_text="Логин пользователя", max_length=64
    )
    password = serializers.CharField(
        help_text="Сгенерированный пароль для первого входа"
    )
    last_name = serializers.CharField(
        help_text="Фамилия пользователя", max_length=32
    )
    first_name = serializers.CharField(
        help_text="Имя пользователя", max_length=32
    )
    patronymic = serializers.CharField(
        help_text="Отчество пользователя", max_length=32
    )
    post = serializers.CharField(
        help_text="Должность пользователя", max_length=128
    )
    is_active = serializers.BooleanField(
        help_text="Активация аккаунта"
    )


class UserUpdateInputSerializer(serializers.Serializer):
    """Сериализатор обновления пользователя"""

    login = serializers.CharField(
        help_text="Логин пользователя", max_length=64, required=False
    )
    last_name = serializers.CharField(
        help_text="Фамилия пользователя", max_length=32, required=False, allow_blank=True
    )
    first_name = serializers.CharField(
        help_text="Имя пользователя", max_length=32, required=False, allow_blank=True
    )
    patronymic = serializers.CharField(
        help_text="Отчество пользователя", max_length=32, required=False, allow_blank=True
    )
    post = serializers.CharField(
        help_text="Должность пользователя", max_length=128, required=False, allow_blank=True
    )
    is_active = serializers.BooleanField(
        help_text="Активация аккаунта", required=False
    )

    def validate_login(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким логином уже существует")
        return value


class UserFullUpdateInputSerializer(serializers.Serializer):
    """Сериализатор полного обновления пользователя"""

    login = serializers.CharField(
        help_text="Логин пользователя", max_length=64, required=True
    )
    last_name = serializers.CharField(
        help_text="Фамилия пользователя", max_length=32, required=True, allow_blank=False
    )
    first_name = serializers.CharField(
        help_text="Имя пользователя", max_length=32, required=True, allow_blank=False
    )
    patronymic = serializers.CharField(
        help_text="Отчество пользователя", max_length=32, required=False, allow_blank=True
    )
    post = serializers.CharField(
        help_text="Должность пользователя", max_length=128, required=True, allow_blank=False
    )
    is_active = serializers.BooleanField(
        help_text="Активация аккаунта", required=False
    )

    def validate_login(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким логином уже существует")
        return value
