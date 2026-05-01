from api.models import AccessNode, AccessSection, AccessObject
from api.v1.services.audit import AuditService


class AccessNodeService:
    """Сервис для работы с узлами доступа"""

    @staticmethod
    def create_node(data: dict, user) -> tuple:
        """Создание узла доступа"""
        try:
            section = AccessSection.objects.get(
                id=data['section_id'],
                is_deleted=False
            )

            node = AccessNode.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                ip=data.get('ip'),
                ip_validated=data.get('ip_validated', False),
                last_validation_error=data.get('last_validation_error', ''),
                section=section
            )

            AuditService.log(user, 'CREATE', node)
            return node, None
        except Exception as e:
            return None, f"Ошибка создания узла: {str(e)}"

    @staticmethod
    def update_node(node, data: dict, user) -> tuple:
        """Обновление узла доступа"""
        try:

            old_node = AccessNode.objects.get(pk=node.pk)

            if 'name' in data:
                node.name = data['name']
            if 'description' in data:
                node.description = data['description']
            if 'ip' in data:
                node.ip = data['ip'] if data['ip'] else None
            if 'ip_validated' in data:
                node.ip_validated = data['ip_validated']
            if 'last_validation_error' in data:
                node.last_validation_error = data['last_validation_error']

            node.save()

            changes = AuditService.model_diff(
                old_node, node,
                fields=['name', 'description', 'ip',
                        'ip_validated', 'last_validation_error']
            )

            if changes:
                AuditService.log(user, 'UPDATE', node, changes)

            return node, None
        except Exception as e:
            return None, f"Ошибка обновления узла: {str(e)}"

    @staticmethod
    def delete_node(node, user) -> tuple:
        """Мягкое удаление узла доступа"""
        if node.is_deleted:
            return False, "Узел уже удален"

        if AccessObject.objects.filter(node=node, is_deleted=False).exists():
            return False, "Невозможно удалить узел, у которого есть объекты доступа"

        node.is_deleted = True
        node.save()
        AuditService.log(user, 'DELETE', node)
        return True, None

    @staticmethod
    def restore_node(node, user) -> tuple:
        """Восстановление узла доступа"""
        if not node.is_deleted:
            return False, "Узел не был удален"

        if AccessNode.objects.filter(
            section=node.section,
            name=node.name,
            is_deleted=False
        ).exclude(id=node.id).exists():
            return False, "Узел с таким именем уже существует в этом разделе"

        node.is_deleted = False
        node.save()
        AuditService.log(user, 'RESTORE', node)
        return True, None
