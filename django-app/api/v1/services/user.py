import secrets
import string

from api.models import User
from api.v1.services.audit import AuditService


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    def generate_password(length: int = 12) -> str:
        """Генерирует пароль пользователя"""

        symbols = string.ascii_letters + string.digits + "!@#$%^&*"
        while True:
            password = ''.join(secrets.choice(symbols) for _ in range(length))
            if (any(symbol.isdigit() for symbol in password) and
                    any(symbol in "!@#$%^&*" for symbol in password)):
                return password

    @staticmethod
    def create_user(data: dict, admin) -> tuple:
        """Создание учетной записи пользователя"""

        login = data.get('login')
        if not login:
            return None, None, "Логин обязателен"

        if User.objects.filter(username=login).exists():
            return None, None, "Пользователь с таким логином уже существует"

        try:
            password = UserService.generate_password()
            user = User.objects.create_user(
                username=login,
                password=password,
                last_name=data.get('last_name', ''),
                first_name=data.get('first_name', ''),
                patronymic=data.get('patronymic', ''),
                is_active=data.get('is_active', False),
            )
            if data.get('is_active', False):
                user.reset_password = True

            user.save()

            AuditService.log(admin, 'CREATE', user)

            return user, password, None

        except Exception as e:
            return None, None, f"Ошибка создания пользователя: {str(e)}"

    @staticmethod
    def update_user(user, data: dict, admin) -> tuple:
        """Обновление учетной записи пользователя"""

        try:

            old_user = User.objects.get(pk=user.pk)

            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'patronymic' in data:
                user.patronymic = data['patronymic']
            if 'login' in data:
                if User.objects.filter(username=data['login']).exclude(id=user.id).exists():
                    return None, "Пользователь с таким логином уже существует"
                user.username = data['login']
            if 'post' in data:
                user.post = data['post']
            if 'is_active' in data:
                user.is_active = data['is_active']
                if data['is_active'] and not user.reset_password:
                    user.reset_password = True

            user.save()

            changes = AuditService.model_diff(
                old_user, user,
                fields=['last_name', 'first_name',
                        'patronymic', 'login', 'post', 'is_active']
            )

            if changes:
                AuditService.log(admin, 'UPDATE', user, changes)

            return user, None

        except Exception as e:
            return None, f"Ошибка обновления пользователя: {str(e)}"

    @staticmethod
    def delete_user(user, admin) -> tuple:
        """Мягкое удаление учетной записи пользователя"""

        if user.is_deleted:
            return False, "Пользователь уже удален"

        user.is_deleted = True
        user.is_active = False
        user.save()
        AuditService.log(admin, 'DELETE', user)
        return True, None

    @staticmethod
    def restore_user(user, admin) -> tuple:
        """Восстановление учетной записи пользователя"""

        if not user.is_deleted:
            return False, "Пользователь не был удален"

        user.is_deleted = False
        user.save()
        AuditService.log(admin, 'RESTORE', user)
        return True, None

    @staticmethod
    def reset_password(user, admin) -> tuple:
        """Сброс пароля пользователя"""

        if not user.is_active:
            return False, "Пользователь должен быть активен"
        password = UserService.generate_password()
        user.set_password(password)
        user.reset_password = True
        user.save()
        AuditService.log(admin, 'RESET_PASS', user)

        return password, None
