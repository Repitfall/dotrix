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
                template=template
            )

            AuditService.log(user, 'CREATE', access_type)
            return access_type, None
        except Exception as e:
            return None, f"Ошибка создания типа доступа: {str(e)}"

    @staticmethod
    def delete_access_type(access_type, user) -> tuple:
        try:
            AuditService.log(user, 'DELETE', access_type)
            access_type.delete()
            return True, None
        except Exception as e:
            return False, f"Ошибка удаления типа доступа: {str(e)}"
