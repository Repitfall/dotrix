from rest_framework import serializers
from api.models import User, AccessRegistry, AccessSection, AccessNode, AccessObject, AccessType


class ErrorOutputSerializer(serializers.Serializer):
    """Сериализатор для отображения ошибок (выходные данные)"""

    error = serializers.CharField(
        help_text="Текст ошибки")
    detail = serializers.CharField(
        help_text="Детали ошибки", required=False)


class StatusOutputSerializer(serializers.Serializer):
    """Сериализатор для статуса API (выходные данные)"""

    status = serializers.CharField(
        help_text="Статус API")


class LoginInputSerializer(serializers.Serializer):
    """Сериализатор для авторизации (входные данные)"""

    login = serializers.CharField(
        help_text="Логин пользователя", max_length=64)
    password = serializers.CharField(
        help_text="Пароль пользователя", max_length=128)


class LoginOutputSerializer(serializers.Serializer):
    """Сериализатор для авторизации (выходные данные)"""

    id = serializers.CharField(
        help_text="Идентификатор пользователя")
    login = serializers.CharField(
        help_text="Логин пользователя")


class UserModelSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя (модель)"""

    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name',
                  'patronymic', 'post', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at']


class ListOutputSerializer(serializers.Serializer):
    """Сериализатор списка (выходные данные)"""

    count = serializers.IntegerField(
        help_text="Общее количество"),
    next = serializers.CharField(
        help_text="Ссылка на следующую страницу", required=False)
    previous = serializers.CharField(
        help_text="Ссылка на предыдущую страницу", required=False)
    results = UserModelSerializer(
        help_text="Список", many=True)


class UserInputSerializer(serializers.Serializer):
    """Сериализатор для профиля пользователя (входные данные)"""

    login = serializers.CharField(
        help_text="Логин", max_length=64)
    last_name = serializers.CharField(
        help_text="Фамилия", max_length=32)
    first_name = serializers.CharField(
        help_text="Имя", max_length=32)
    patronymic = serializers.CharField(
        help_text="Отчество", max_length=32)
    is_active = serializers.BooleanField(
        help_text="Активация аккаунта", required=False)

    def validate_login(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким логином уже существует")
        return value


class UserOutputSerializer(serializers.Serializer):
    """Сериализатор для профиля пользователя (выходные данные)"""

    id = serializers.CharField(
        help_text="Идентификатор пользователя")
    login = serializers.CharField(
        help_text="Логин пользователя", max_length=64)
    last_name = serializers.CharField(
        help_text="Фамилия", max_length=32, required=False)
    first_name = serializers.CharField(
        help_text="Имя", max_length=32, required=False)
    patronymic = serializers.CharField(
        help_text="Отчество", max_length=32, required=False)
    is_active = serializers.BooleanField(
        help_text="Активация аккаунта", required=False)


class CreateUserOutputSerializer(serializers.Serializer):
    """Сериализатор для профиля пользователя (выходные данные)"""

    id = serializers.IntegerField(
        help_text="Идентификатор пользователя")
    login = serializers.CharField(
        help_text="Логин пользователя", max_length=64)
    password = serializers.CharField(
        help_text="Сгенерированный пароль пользователя", max_length=128)
    last_name = serializers.CharField(
        help_text="Фамилия", max_length=32, required=False)
    first_name = serializers.CharField(
        help_text="Имя", max_length=32, required=False)
    patronymic = serializers.CharField(
        help_text="Отчество", max_length=32, required=False)


class AccessRegistryModelSerializer(serializers.ModelSerializer):
    """Сериализатор регистра доступов (модель)"""

    class Meta:
        model = AccessRegistry
        fields = ['id', 'name']


class AccessRegistryInputSerializer(serializers.Serializer):
    """Сериализатор для реестра доступа (входные данные)"""

    name = serializers.CharField(
        help_text="Название", max_length=64)


class AccessRegistryOutputSerializer(serializers.Serializer):
    """Сериализатор для реестра доступа (выходна данные)"""

    id = serializers.CharField(
        help_text="Идентификатор реестра доступа")
    name = serializers.CharField(
        help_text="Название", max_length=64)


class AccessSectionModelSerializer(serializers.ModelSerializer):
    """Сериализатор раздела доступов (модель)"""

    class Meta:
        model = AccessSection
        fields = ['id', 'name']


class AccessNodeModelSerializer(serializers.ModelSerializer):
    """Сериализатор узла доступов (модель)"""

    class Meta:
        model = AccessNode
        fields = ['id', 'name']


class AccessObjectModelSerializer(serializers.ModelSerializer):
    """Сериализатор объекта доступов (модель)"""

    class Meta:
        model = AccessObject
        fields = ['id', 'name']


class AccessTypeModelSerializer(serializers.ModelSerializer):
    """Сериализатор типа доступов (модель)"""

    class Meta:
        model = AccessType
        fields = ['id', 'name']
