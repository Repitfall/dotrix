from api.models import AccessTypeTemplate, AccessType
from api.v1.services.audit import AuditService


class AccessTypeTemplateService:
    """Сервис для работы с шаблонами типов доступа"""

    @staticmethod
    def create_template(data: dict, user) -> tuple:
        """Создание шаблонов типов доступа"""
        try:
            template = AccessTypeTemplate.objects.create(
                name=data['name'],
                description=data.get('description', '')
            )
            AuditService.log(user, 'CREATE', template)
            return template, None
        except Exception as e:
            return None, f"Ошибка создания шаблона: {str(e)}"

    @staticmethod
    def update_template(template, data: dict, user) -> tuple:
        """Обновление шаблонов типов доступа"""
        try:

            old_template = AccessTypeTemplate.objects.get(pk=template.pk)

            if 'name' in data:
                template.name = data['name']
            if 'description' in data:
                template.description = data['description']
            template.save()

            changes = AuditService.model_diff(
                old_template, template,
                fields=['name', 'description']
            )

            if changes:
                AuditService.log(user, 'UPDATE', template, changes)

            return template, None
        except Exception as e:
            return None, f"Ошибка обновления шаблона: {str(e)}"

    @staticmethod
    def delete_template(template, user) -> tuple:
        """Мягкое удаление шаблонов типов доступа"""
        if template.is_deleted:
            return False, "Шаблон уже удалён"

        if AccessType.objects.filter(template=template, is_deleted=False).exists():
            return False, "Невозможно удалить шаблон, так как он используется в типах доступа"

        template.is_deleted = True
        template.save()
        AuditService.log(user, 'DELETE', template)
        return True, None

    @staticmethod
    def restore_template(template, user) -> tuple:
        """Восстановление шаблонов типов доступа"""
        if not template.is_deleted:
            return False, "Шаблон не был удалён"

        if AccessTypeTemplate.objects.filter(name=template.name, is_deleted=False).exclude(id=template.id).exists():
            return False, "Шаблон с таким именем уже существует"

        template.is_deleted = False
        template.save()
        AuditService.log(user, 'RESTORE', template)
        return True, None
