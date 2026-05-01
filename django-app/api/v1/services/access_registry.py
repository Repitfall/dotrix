from api.models import AccessRegistry, AccessGroup
from api.v1.services.audit import AuditService


class AccessRegistryService:
    """Сервис для работы с реестрами доступа"""

    @staticmethod
    def create_registry(data: dict, user) -> tuple:
        """Создание реестра доступа"""
        try:
            registry = AccessRegistry.objects.create(
                name=data['name'],
                description=data.get('description', '')
            )

            owner_group_ids = data.get('owner_group_ids', [])
            if owner_group_ids:
                owner_groups = AccessGroup.objects.filter(
                    id__in=owner_group_ids,
                    is_deleted=False
                )
                registry.owner_groups.set(owner_groups)

            AuditService.log(user, 'CREATE', registry)
            return registry, None
        except Exception as e:
            return None, f"Ошибка создания реестра доступа: {str(e)}"

    @staticmethod
    def update_registry(registry, data: dict, user) -> tuple:
        """Обновление реестра доступа"""
        try:

            old_registry = AccessRegistry.objects.get(pk=registry.pk)

            if 'name' in data:
                registry.name = data['name']
            if 'description' in data:
                registry.description = data['description']

            registry.save()

            if 'owner_group_ids' in data:
                owner_group_ids = data['owner_group_ids']
                if owner_group_ids:
                    owner_groups = AccessGroup.objects.filter(
                        id__in=owner_group_ids,
                        is_deleted=False
                    )
                    registry.owner_groups.set(owner_groups)
                else:
                    registry.owner_groups.clear()

            changes = AuditService.model_diff(
                old_registry, registry,
                fields=['name', 'description', 'owner_groups']
            )

            if changes:
                AuditService.log(user, 'UPDATE', registry, changes)

            return registry, None
        except Exception as e:
            return None, f"Ошибка обновления реестра: {str(e)}"

    @staticmethod
    def delete_registry(registry, user) -> tuple:
        """Мягкое удаление реестра доступа"""
        if registry.is_deleted:
            return False, "Реестр уже удален"

        registry.is_deleted = True
        registry.save()
        AuditService.log(user, 'DELETE', registry)
        return True, None

    @staticmethod
    def restore_registry(registry, user) -> tuple:
        """Восстановление реестра доступа"""
        if not registry.is_deleted:
            return False, "Реестр не был удален"

        registry.is_deleted = False
        registry.save()
        AuditService.log(user, 'RESTORE', registry)
        return True, None
