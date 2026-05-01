from rest_framework import serializers


class ExportRegistrySerializer(serializers.Serializer):
    """Сериализатор экспорта матриц доступа"""

    group_ids = serializers.ListField(
        help_text="ID групп для фильтрации",
        child=serializers.IntegerField(),
        required=False,
    )
    section_ids = serializers.ListField(
        help_text="ID разделов",
        child=serializers.IntegerField(),
        required=False
    )
    node_ids = serializers.ListField(
        help_text="ID узлов",
        child=serializers.IntegerField(),
        required=False,
    )
    object_ids = serializers.ListField(
        help_text="ID объектов",
        child=serializers.IntegerField(),
        required=False
    )
