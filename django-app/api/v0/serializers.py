from rest_framework import serializers
from api.models import User, AccessRegistry, AccessSection, AccessNode, AccessObject, AccessType


#####
# --- Системное
#####


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


class ListOutputSerializer(serializers.Serializer):
    """Сериализатор списка (выходные данные)"""

    count = serializers.IntegerField(
        help_text="Общее количество"),
    next = serializers.CharField(
        help_text="Ссылка на следующую страницу", required=False)
    previous = serializers.CharField(
        help_text="Ссылка на предыдущую страницу", required=False)


#####
# --- Авторизация
#####


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


#####
# --- Пользователь
#####


class UserModelSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя (модель)"""

    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name',
                  'patronymic', 'post', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at']


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


class UserOutputListSerializer(ListOutputSerializer):
    results = UserModelSerializer(
        help_text="Список пользователей", many=True)


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


#####
# --- Реестр доступа
#####


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
    """Сериализатор для реестра доступа (выходные данные)"""

    id = serializers.CharField(
        help_text="Идентификатор реестра доступа")
    name = serializers.CharField(
        help_text="Название", max_length=64)
    is_deleted = serializers.BooleanField(
        help_text="Мягкое удаление объекта", required=False)


class AccessRegistryOutputListSerializer(ListOutputSerializer):
    results = AccessRegistryModelSerializer(
        help_text="Список реестров доступа", many=True)


#####
# --- Раздел доступа
#####


class AccessSectionModelSerializer(serializers.ModelSerializer):
    """Сериализатор раздела доступов (модель)"""

    class Meta:
        model = AccessSection
        fields = ['id', 'registry', 'name']


class AccessSectionOutputSerializer(serializers.Serializer):
    """Сериализатор для раздела доступа (выходные данные)"""

    id = serializers.CharField(
        help_text="Идентификатор раздела доступа")
    registry = serializers.CharField(
        help_text="Идентификатор реестра доступа")
    name = serializers.CharField(
        help_text="Название", max_length=64)


class AccessSectionInputSerializer(serializers.Serializer):
    """Сериализатор для раздела доступа (входные данные)"""

    registry = serializers.IntegerField(
        help_text="Идентификатор реестра доступа")
    name = serializers.CharField(
        help_text="Название", max_length=64)


class AccessSectionOutputListSerializer(ListOutputSerializer):
    results = AccessSectionModelSerializer(
        help_text="Список разделов доступа", many=True)


#####
# --- Узел доступа
#####


class AccessNodeModelSerializer(serializers.ModelSerializer):
    """Сериализатор узла доступов (модель)"""

    class Meta:
        model = AccessNode
        fields = ['id', 'name']


class AccessNodeOutputListSerializer(ListOutputSerializer):
    results = AccessNodeModelSerializer(
        help_text="Список узлов доступа", many=True)


class AccessNodeInputSerializer(serializers.Serializer):
    """Сериализатор для узлов доступа (входные данные)"""

    section = serializers.IntegerField(
        help_text="Идентификатор раздела доступа")
    name = serializers.CharField(
        help_text="Название", max_length=64)


#####
# --- Объект доступа
#####


class AccessObjectModelSerializer(serializers.ModelSerializer):
    """Сериализатор объекта доступов (модель)"""

    class Meta:
        model = AccessObject
        fields = ['id', 'name']


class AccessObjectOutputListSerializer(ListOutputSerializer):
    results = AccessObjectModelSerializer(
        help_text="Список объектов доступа", many=True)


class AccessObjectInputSerializer(serializers.Serializer):
    """Сериализатор для объектов доступа (входные данные)"""

    node = serializers.IntegerField(
        help_text="Идентификатор узла доступа")
    name = serializers.CharField(
        help_text="Название", max_length=64)


#####
# --- Тип доступа
#####


class AccessTypeModelSerializer(serializers.ModelSerializer):
    """Сериализатор типа доступов (модель)"""

    class Meta:
        model = AccessType
        fields = ['id', 'name']


class AccessTypeOutputListSerializer(ListOutputSerializer):
    results = AccessTypeModelSerializer(
        help_text="Список типов доступа", many=True)


class AccessTypeInputSerializer(serializers.Serializer):
    """Сериализатор для типов доступа (входные данные)"""

    object = serializers.IntegerField(
        help_text="Идентификатор объекта доступа")
    name = serializers.CharField(
        help_text="Название", max_length=64)
