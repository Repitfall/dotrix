from django.forms.models import model_to_dict
from django.contrib.contenttypes.models import ContentType

from api.models import AuditEntry


class AuditService:
    @staticmethod
    def log(user, action, instance, changes=None):
        """Сервис для занесения записи в аудит"""
        content_type = ContentType.objects.get_for_model(instance)
        registry = AuditService._get_registry(instance)

        AuditEntry.objects.create(
            user=user if user and user.is_authenticated else None,
            action=action,
            content_type=content_type,
            object_id=instance.pk,
            object_repr=str(instance),
            changes=changes or {},
            registry=registry
        )

    @staticmethod
    def _get_registry(instance):
        """Извлекает реестр из объекта"""

        if hasattr(instance, 'registry_id'):
            return instance.registry
        if hasattr(instance, 'section') and hasattr(instance.section, 'registry'):
            return instance.section.registry
        if hasattr(instance, 'node') and hasattr(instance.node.section, 'registry'):
            return instance.node.section.registry
        if hasattr(instance, 'object') and hasattr(instance.object.node.section, 'registry'):
            return instance.object.node.section.registry
        if hasattr(instance, 'access_type') and hasattr(instance.access_type.object.node.section, 'registry'):
            return instance.access_type.object.node.section.registry
        return None

    @staticmethod
    def model_diff(old_instance, new_instance, fields=None, exclude=None):
        """Сравнивает два состояния модели и возвращает изменения"""
        if exclude is None:
            exclude = ['id']

        old_dict = model_to_dict(old_instance, fields=fields, exclude=exclude)
        new_dict = model_to_dict(new_instance, fields=fields, exclude=exclude)

        changes = {}
        for field in fields or old_dict.keys():
            old_val = old_dict.get(field)
            new_val = new_dict.get(field)

            if hasattr(old_val, 'all'):
                old_val = list(old_val.values_list('id', flat=True))
            if hasattr(new_val, 'all'):
                new_val = list(new_val.values_list('id', flat=True))

            if old_val != new_val:
                changes[field] = {'old': old_val, 'new': new_val}

        return changes
