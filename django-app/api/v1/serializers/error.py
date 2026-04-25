from rest_framework import serializers


class ErrorOutputSerializer(serializers.Serializer):
    """Сериализатор ошибки"""

    error = serializers.CharField(
        help_text="Краткое описание ошибки"
    )
    detail = serializers.CharField(
        help_text="Детальное описание ошибки",
        required=False
    )
