from api.models import AccessNode, AccessSection, AccessObject


class AccessNodeService:
    """Сервис для работы с узлами доступа"""

    @staticmethod
    def create_node(data: dict) -> tuple:
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

            return node, None
        except Exception as e:
            return None, f"Ошибка создания узла: {str(e)}"

    @staticmethod
    def update_node(node, data: dict) -> tuple:
        """Обновление узла доступа"""
        try:
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
            return node, None
        except Exception as e:
            return None, f"Ошибка обновления узла: {str(e)}"

    @staticmethod
    def delete_node(node) -> tuple:
        """Мягкое удаление узла доступа"""
        if node.is_deleted:
            return False, "Узел уже удален"

        if AccessObject.objects.filter(node=node, is_deleted=False).exists():
            return False, "Невозможно удалить узел, у которого есть объекты доступа"

        node.is_deleted = True
        node.save()
        return True, None

    @staticmethod
    def restore_node(node) -> tuple:
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
        return True, None
