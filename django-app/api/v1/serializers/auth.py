from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


class LoginInputSerializer(serializers.Serializer):
    """Сериализатор авторизации пользователя"""

    login = serializers.CharField(
        help_text="Логин пользователя",
        max_length=64,
        write_only=True
    )
    password = serializers.CharField(
        help_text="Пароль пользователя",
        max_length=128,
        write_only=True,
        style={'input_type': 'password'}
    )


class LoginOutputSerializer(serializers.Serializer):
    """Сериализатор авторизации пользователя"""

    id = serializers.IntegerField(
        help_text="ID пользователя"
    )
    login = serializers.CharField(
        help_text="Логин пользователя"
    )


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля пользователя"""

    login = serializers.CharField(
        help_text="Логин пользователя",
        max_length=64,
        write_only=True
    )
    old_password = serializers.CharField(
        help_text="Старый пароль",
        max_length=128,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        help_text="Новый пароль",
        max_length=128,
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
