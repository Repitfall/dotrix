from rest_framework import serializers


class StatusOutputSerializer(serializers.Serializer):
    """Сериализатор статуса сервера"""

    status = serializers.CharField(
        help_text="Статус сервера"
    )
