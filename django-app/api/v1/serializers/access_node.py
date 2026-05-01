import socket
from rest_framework import serializers
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError

from api.models import AccessNode, AccessSection


class AccessNodeModelSerializer(serializers.ModelSerializer):
    """Сериализатор вывода информации об узле доступа"""

    section_name = serializers.CharField(
        source='section.name',
        read_only=True
    )
    registry_name = serializers.CharField(
        source='section.registry.name',
        read_only=True
    )
    has_warning = serializers.SerializerMethodField()

    class Meta:
        model = AccessNode
        fields = ['id', 'name', 'description', 'ip',
                  'section', 'section_name', 'registry_name',
                  'ip_validated', 'last_validation_error', 'has_warning']
        read_only_fields = ['id', 'ip_validated', 'last_validation_error']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request = self.context.get('request')

        if request and request.user.is_staff:
            representation['is_deleted'] = instance.is_deleted

        return representation

    def get_has_warning(self, obj):
        """Есть ли предупреждение о валидации"""
        return not obj.ip_validated and obj.last_validation_error


class AccessNodeCreateInputSerializer(serializers.Serializer):
    """Сериализатор создания узла доступа"""

    name = serializers.CharField(
        help_text="Доменное имя узла",
        max_length=128
    )
    description = serializers.CharField(
        help_text="Описание",
        required=False,
        allow_blank=True
    )
    ip = serializers.CharField(
        help_text="IP-адрес",
        required=False,
        allow_blank=True,
        allow_null=True
    )
    section_id = serializers.IntegerField(
        help_text="ID раздела доступа"
    )

    def validate_section_id(self, value):
        """Проверка существования раздела"""
        if not AccessSection.objects.filter(id=value, is_deleted=False).exists():
            raise serializers.ValidationError("Раздел не найден")
        return value

    def validate_name(self, value):
        """Проверка уникальности имени в рамках раздела"""
        section_id = self.initial_data.get('section_id')
        if section_id:
            if AccessNode.objects.filter(
                section_id=section_id,
                name=value,
                is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    "Узел с таким именем уже существует в этом разделе"
                )
        return value

    def validate(self, data):
        """Комплексная валидация с предупреждениями"""
        name = data.get('name')
        ip = data.get('ip')
        warnings = []

        if name:
            try:
                resolved_ip = socket.gethostbyname(name)

                if not ip:
                    data['ip'] = resolved_ip
                    data['ip_validated'] = True
                    data['last_validation_error'] = ''
                else:
                    if ip != resolved_ip:
                        warnings.append({
                            'field': 'ip',
                            'message': f'IP {ip} не соответствует домену {name} (разрешился в {resolved_ip})'
                        })
                        data['ip_validated'] = False
                        data['last_validation_error'] = warnings[-1]['message']
                    else:
                        data['ip_validated'] = True
                        data['last_validation_error'] = ''

            except socket.gaierror as e:
                warnings.append({
                    'field': 'name',
                    'message': f'Домен {name} не разрешается: {str(e)}'
                })
                data['ip_validated'] = False
                data['last_validation_error'] = warnings[-1]['message']

        if ip and not data.get('ip_validated'):
            try:
                validate_ipv4_address(ip)
                data['ip'] = ip
            except ValidationError:
                warnings.append({
                    'field': 'ip',
                    'message': f'Неверный формат IP-адреса: {ip}'
                })
                data['last_validation_error'] = warnings[-1]['message']

        if warnings:
            data['ip_validated'] = False
            data['last_validation_error'] = warnings[-1]['message']
        else:
            data['ip_validated'] = True
            data['last_validation_error'] = ''

        return data


class AccessNodeCreateOutputSerializer(serializers.Serializer):
    """Сериализатор создания узла доступа"""

    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    ip = serializers.CharField(
        allow_null=True
    )
    section_id = serializers.IntegerField()
    ip_validated = serializers.BooleanField()
    last_validation_error = serializers.CharField(
        allow_null=True
    )
    warnings = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class AccessNodeUpdateInputSerializer(serializers.Serializer):
    """Сериализатор обновления узла доступа"""

    name = serializers.CharField(
        help_text="Доменное имя узла",
        max_length=128,
        required=False
    )
    description = serializers.CharField(
        help_text="Описание",
        required=False,
        allow_blank=True
    )
    ip = serializers.CharField(
        help_text="IP-адрес",
        required=False,
        allow_blank=True,
        allow_null=True
    )

    def validate_name(self, value):
        """Проверка уникальности имени в рамках раздела"""
        if value and self.instance:
            if AccessNode.objects.exclude(id=self.instance.id).filter(
                section=self.instance.section,
                name=value,
                is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    "Узел с таким именем уже существует в этом разделе"
                )
        return value

    def validate(self, data):
        """Комплексная валидация с предупреждениями"""
        name = data.get('name', self.instance.name if self.instance else None)
        ip = data.get('ip')

        update_ip = 'ip' in data
        current_ip = self.instance.ip if self.instance else None

        warnings = []

        if name:
            try:
                resolved_ip = socket.gethostbyname(name)

                if not update_ip:
                    pass
                elif ip is None:
                    data['ip'] = None
                    data['ip_validated'] = False
                    data['last_validation_error'] = 'IP адрес очищен'
                elif ip == '':
                    data['ip'] = None
                    data['ip_validated'] = False
                    data['last_validation_error'] = 'IP адрес очищен'
                elif ip != resolved_ip:
                    warnings.append({
                        'field': 'ip',
                        'message': f'IP {ip} не соответствует домену {name} (разрешился в {resolved_ip})'
                    })
                    data['ip'] = ip
                    data['ip_validated'] = False
                    data['last_validation_error'] = warnings[-1]['message']
                else:
                    data['ip'] = ip
                    data['ip_validated'] = True
                    data['last_validation_error'] = ''

            except socket.gaierror as e:
                if update_ip:
                    warnings.append({
                        'field': 'name',
                        'message': f'Домен {name} не разрешается: {str(e)}'
                    })
                    data['ip_validated'] = False
                    data['last_validation_error'] = warnings[-1]['message']
                else:
                    pass

        if update_ip and ip and not name and self.instance:
            if ip != self.instance.ip:
                data['ip_validated'] = False
                data['last_validation_error'] = 'IP адрес изменён вручную'

        if warnings:
            data['ip_validated'] = False
            data['last_validation_error'] = warnings[-1]['message']
        else:
            data['ip_validated'] = True
            data['last_validation_error'] = ''

        return data
