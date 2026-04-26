from api.models import AccessObject, AccessNode, AccessType


class AccessObjectService:
    """Сервис для работы с объектами доступа"""

    @staticmethod
    def create_object(data: dict) -> tuple:
        """Создание объекта доступа"""
        try:
            node = AccessNode.objects.get(id=data['node_id'], is_deleted=False)

            obj = AccessObject.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                resource_path=data['resource_path'],
                node=node
            )
            return obj, None
        except Exception as e:
            return None, f"Ошибка создания объекта: {str(e)}"

    @staticmethod
    def update_object(obj, data: dict) -> tuple:
        """Обновление объекта доступа"""
        try:
            if 'node_id' in data:
                return None, "Изменение узла объекта запрещено"

            if 'name' in data:
                obj.name = data['name']
            if 'description' in data:
                obj.description = data['description']
            if 'resource_path' in data:
                obj.resource_path = data['resource_path']

            obj.save()
            return obj, None
        except Exception as e:
            return None, f"Ошибка обновления объекта: {str(e)}"

    @staticmethod
    def delete_object(obj) -> tuple:
        """Мягкое удаление объекта доступа"""
        if obj.is_deleted:
            return False, "Объект уже удален"

        if AccessType.objects.filter(object=obj, is_deleted=False).exists():
            return False, "Невозможно удалить объект, у которого есть типы доступа"

        obj.is_deleted = True
        obj.save()
        return True, None

    @staticmethod
    def restore_object(obj) -> tuple:
        """Восстановление объекта доступа"""
        if not obj.is_deleted:
            return False, "Объект не был удален"

        if AccessObject.objects.filter(
            node=obj.node,
            name=obj.name,
            is_deleted=False
        ).exclude(id=obj.id).exists():
            return False, "Объект с таким именем уже существует на этом узле"

        obj.is_deleted = False
        obj.save()
        return True, None
