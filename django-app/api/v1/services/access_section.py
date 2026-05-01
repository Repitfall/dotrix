from api.models import AccessSection, AccessRegistry
from api.v1.services.audit import AuditService


class AccessSectionService:
    """Сервис для работы с разделами доступа"""

    @staticmethod
    def create_section(data: dict, user) -> tuple:
        """Создание раздела доступа"""
        try:
            registry = AccessRegistry.objects.get(
                id=data['registry_id'],
                is_deleted=False
            )

            section = AccessSection.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                registry=registry
            )

            AuditService.log(user, 'CREATE', section)
            return section, None
        except Exception as e:
            return None, f"Ошибка создания раздела: {str(e)}"

    @staticmethod
    def update_section(section, data: dict, user) -> tuple:
        """Обновление раздела доступа"""
        try:

            old_section = AccessSection.objects.get(pk=section.pk)

            if 'name' in data:
                section.name = data['name']
            if 'description' in data:
                section.description = data['description']

            changes = AuditService.model_diff(
                old_section, section,
                fields=['name', 'description']
            )
            if changes:
                AuditService.log(user, 'UPDATE', section, changes)

            section.save()
            return section, None
        except Exception as e:
            return None, f"Ошибка обновления раздела: {str(e)}"

    @staticmethod
    def delete_section(section, user) -> tuple:
        """Мягкое удаление раздела доступа"""
        if section.is_deleted:
            return False, "Раздел уже удален"

        if section.nodes.filter(is_deleted=False).exists():
            return False, "Невозможно удалить раздел, у которого есть узлы"

        section.is_deleted = True
        section.save()
        AuditService.log(user, 'DELETE', section)
        return True, None

    @staticmethod
    def restore_section(section, user) -> tuple:
        """Восстановление раздела доступа"""
        if not section.is_deleted:
            return False, "Раздел не был удален"

        if AccessSection.objects.filter(
            registry=section.registry,
            name=section.name,
            is_deleted=False
        ).exclude(id=section.id).exists():
            return False, "Раздел с таким именем уже существует в этом реестре"

        section.is_deleted = False
        section.save()
        AuditService.log(user, 'RESTORE', section)
        return True, None
