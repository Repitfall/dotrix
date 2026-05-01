from django.utils import timezone

from api.models import AccessRight, AccessType, AccessGroup
from api.v1.services.audit import AuditService


class AccessRightService:
    """Сервис для работы с назначениями прав группам"""

    @staticmethod
    def create_access_right(data: dict, granted_by) -> tuple:
        """Создание права"""
        try:
            access_type = AccessType.objects.get(
                id=data['access_type_id'], is_deleted=False)
            group = AccessGroup.objects.get(
                id=data['group_id'], is_deleted=False)

            access_right = AccessRight.objects.create(
                access_type=access_type,
                group=group,
                granted_by=granted_by,
                expires_at=data.get('expires_at')
            )
            AuditService.log(granted_by, 'CREATE', access_right)
            return access_right, None
        except Exception as e:
            return None, f"Ошибка назначения права: {str(e)}"

    @staticmethod
    def update_access_right(access_right, data: dict, user) -> tuple:
        """Обновление права"""
        try:

            old_right = AccessRight.objects.get(pk=access_right.pk)

            if 'expires_at' in data:
                access_right.expires_at = data['expires_at']
            access_right.save()

            changes = AuditService.model_diff(
                old_right, access_right,
                fields=['expires_at']
            )

            if changes:
                AuditService.log(user, 'UPDATE', access_right, changes)

            return access_right, None
        except Exception as e:
            return None, f"Ошибка обновления права: {str(e)}"

    @staticmethod
    def delete_access_right(access_right, user) -> tuple:
        """Полное удаление права"""
        try:
            access_right.delete()
            AuditService.log(user, 'DELETE', access_right)
            return True, None
        except Exception as e:
            return False, f"Ошибка отзыва права: {str(e)}"
