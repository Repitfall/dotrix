from api.models import AccessType, AccessObject, AccessTypeTemplate, AccessRight
from api.v1.services.audit import AuditService


class AccessTypeService:
    """Сервис для работы с типами доступа"""

    @staticmethod
    def create_access_type(data: dict, user) -> tuple:
        try:
            obj = AccessObject.objects.get(
                id=data['object_id'],
                is_deleted=False
            )
            template = AccessTypeTemplate.objects.get(
                id=data['template_id'],
                is_deleted=False
            )

            access_type = AccessType.objects.create(
                object=obj,
                template=template,
                is_deleted=False
            )

            AuditService.log(user, 'CREATE', access_type)
            return access_type, None
        except Exception as e:
            return None, f"Ошибка создания типа доступа: {str(e)}"

    @staticmethod
    def delete_access_type(access_type, user) -> tuple:
        """Мягкое удаление типа доступа"""
        if access_type.is_deleted:
            return False, "Тип доступа уже удалён"

        if AccessRight.objects.filter(access_type=access_type).exists():
            return False, "Невозможно удалить тип доступа, так как он назначен группам"

        access_type.is_deleted = True
        access_type.save()
        AuditService.log(user, 'DELETE', access_type)
        return True, None

    @staticmethod
    def restore_access_type(access_type, user) -> tuple:
        """Восстановление типа доступа"""
        if not access_type.is_deleted:
            return False, "Тип доступа не был удалён"

        if AccessType.objects.filter(
            object=access_type.object,
            template=access_type.template,
            is_deleted=False
        ).exclude(id=access_type.id).exists():
            return False, "Тип доступа для этого объекта и шаблона уже существует"

        access_type.is_deleted = False
        access_type.save()
        AuditService.log(user, 'RESTORE', access_type)
        return True, None
