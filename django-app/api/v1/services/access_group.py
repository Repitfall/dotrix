from api.models import AccessGroup, AccessRegistry, User


class AccessGroupService:
    """Сервис для работы с группами доступа"""

    @staticmethod
    def create_group(data: dict) -> tuple:
        """Создание группы доступа"""
        try:
            registry = AccessRegistry.objects.get(
                id=data['registry_id'],
                is_deleted=False
            )

            if data.get('parent_group_id'):
                max_depth = 10
                parent = AccessGroup.objects.get(
                    id=data['parent_group_id'],
                    is_deleted=False
                )
                depth = 1
                current = parent
                while current.parent_group:
                    depth += 1
                    current = current.parent_group
                    if depth > max_depth:
                        return None, f"Превышена максимальная глубина иерархии ({max_depth} уровней)"

            group = AccessGroup.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                registry=registry,
                parent_group_id=data.get('parent_group_id'),
            )

            user_ids = data.get('user_ids', [])
            if user_ids:
                users = User.objects.filter(id__in=user_ids, is_deleted=False)
                group.users.set(users)

            owner_registry_ids = data.get('owner_of_registry_ids', [])
            if owner_registry_ids:
                registries = AccessRegistry.objects.filter(
                    id__in=owner_registry_ids,
                    is_deleted=False
                )
                group.owned_registries.set(registries)

            return group, None
        except Exception as e:
            return None, f"Ошибка создания группы: {str(e)}"

    @staticmethod
    def update_group(group, data: dict) -> tuple:
        """Обновление группы доступа"""
        try:
            if 'registry_id' in data and data['registry_id'] != group.registry_id:
                return None, "Изменение реестра группы запрещено"
            if 'name' in data:
                group.name = data['name']
            if 'description' in data:
                group.description = data['description']
            if 'parent_group_id' in data and data['parent_group_id']:
                parent_group_id = data['parent_group_id']

                if parent_group_id:
                    try:
                        parent = AccessGroup.objects.get(
                            id=parent_group_id, is_deleted=False)
                    except AccessGroup.DoesNotExist:
                        return None, "Родительская группа не найдена"

                    max_depth = 10
                    depth = 1
                    current = parent
                    while current.parent_group:
                        depth += 1
                        current = current.parent_group
                        if depth > max_depth:
                            return f"Превышена максимальная глубина иерархии ({max_depth} уровней)"

                    group.parent_group_id = data['parent_group_id']

            group.save()

            if 'user_ids' in data:
                if data['user_ids']:
                    users = User.objects.filter(
                        id__in=data['user_ids'], is_deleted=False)
                    group.users.set(users)
                else:
                    group.users.clear()

            if 'owner_of_registry_ids' in data:
                if data['owner_of_registry_ids']:
                    registries = AccessRegistry.objects.filter(
                        id__in=data['owner_of_registry_ids'],
                        is_deleted=False
                    )
                    group.owned_registries.set(registries)
                else:
                    group.owned_registries.clear()

            return group, None
        except Exception as e:
            return None, f"Ошибка обновления группы: {str(e)}"

    @staticmethod
    def delete_group(group) -> tuple:
        """Мягкое удаление группы доступа"""
        if group.is_deleted:
            return False, "Группа уже удалена"

        if group.child_groups.filter(is_deleted=False).exists():
            return False, "Невозможно удалить группу, у которой есть подгруппы"

        if group.get_all_users():
            return False, "Невозможно удалить группу, в которой есть пользователи"

        if group.owned_registries.filter(is_deleted=False).exists():
            return False, "Невозможно удалить группу, которая является руководителем реестра"

        group.is_deleted = True
        group.save()
        return True, None

    @staticmethod
    def restore_group(group) -> tuple:
        """Восстановление группы доступа"""
        if not group.is_deleted:
            return False, "Группа не была удалена"

        if AccessGroup.objects.filter(
            registry=group.registry,
            name=group.name,
            is_deleted=False
        ).exclude(id=group.id).exists():
            return False, "Группа с таким именем уже существует в этом реестре"

        group.is_deleted = False
        group.save()
        return True, None
