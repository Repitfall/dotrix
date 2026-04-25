from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешение только для администраторов"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение только для администраторам, GET доступен только авторизованным"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


class CanViewRegistry(permissions.BasePermission):
    """Разрешение на просмотр реестра доступа"""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.access_groups.filter(
            registry=obj.id,
            is_deleted=False
        ).exists():
            return True

        return request.user.is_staff


class CanEditRegistry(permissions.BasePermission):
    """Разрешение на редактирование реестра доступа"""
    # Может понадобиться в будущем

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.access_groups.filter(
            owned_registries=obj,
            is_deleted=False
        ).exists():
            return True


class CanManageGroup(permissions.BasePermission):
    """Разрешение на управление группой"""
    # Может понадобиться в будущем

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        return request.user.access_groups.filter(
            owned_registries=obj.registry,
            is_deleted=False
        ).exists()
