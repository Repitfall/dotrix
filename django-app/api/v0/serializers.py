from rest_framework import serializers


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
    username = serializers.CharField(
        help_text="Логин", max_length=64)
    password = serializers.CharField(
        help_text="Пароль", max_length=128)


class LoginOutputSerializer(serializers.Serializer):
    """Сериализатор для авторизации (выходные данные)"""
    access_token = serializers.CharField(
        help_text="Access-токен")
    refresh_token = serializers.CharField(
        help_text="Refresh-токен")
    user_id = serializers.CharField(
        help_text="ID пользователя")
    login = serializers.CharField(
        help_text="Логин пользователя")
    api_version = serializers.CharField(
        help_text="Версия API")


class ProfileOutputSerializer(serializers.Serializer):
    """Сериализатор для просмотра своего профиля (выходные данные)"""
    last_name = serializers.CharField(
        help_text="Фамилия", max_length=32, required=False)
    first_name = serializers.CharField(
        help_text="Имя", max_length=32, required=False)
    patronymic = serializers.CharField(
        help_text="Отчество", max_length=32, required=False)
