from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    """Модель пользователя"""

    username = models.CharField(
        verbose_name="Логин",
        max_length=64,
        unique=True,
        validators=[MinLengthValidator(3)]
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=32
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=32
    )
    patronymic = models.CharField(
        verbose_name="Отчество",
        max_length=32,
        blank=True
    )
    post = models.CharField(
        verbose_name="Должность",
        max_length=128
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True
    )

    auth_offline = models.BooleanField(
        verbose_name="Автономная авторизация",
        default=True
    )
    reset_password = models.BooleanField(
        verbose_name="Сброс пароля",
        default=False
    )
    is_active = models.BooleanField(
        default=False
    )
    is_deleted = models.BooleanField(
        default=False
    )

    access_groups = models.ManyToManyField(
        'AccessGroup',
        verbose_name="Группы доступа",
        related_name='users',
        blank=True
    )

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['is_active', 'is_deleted']),
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"


class AccessRegistry(models.Model):
    """Модель реестра доступа (первый уровень иерархии доступов)"""

    name = models.CharField(
        verbose_name="Название",
        max_length=64,
        unique=True
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True
    )

    owner_groups = models.ManyToManyField(
        'AccessGroup',
        verbose_name="Группы руководителей",
        related_name='owned_registries',
        blank=True,
    )

    is_deleted = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = "Реестр доступа"
        verbose_name_plural = "Реестры доступа"
        ordering = ['name']

    def __str__(self):
        return self.name


class AccessGroup(models.Model):
    """Модель группы доступа пользователей (внутри реестра доступа)"""

    registry = models.ForeignKey(
        AccessRegistry,
        verbose_name="Реестр доступа",
        related_name='groups',
        on_delete=models.PROTECT,
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=64
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True
    )

    parent_group = models.ForeignKey(
        'self',
        verbose_name="Родительская группа",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='child_groups'
    )

    is_deleted = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = "Группа доступа"
        verbose_name_plural = "Группы доступа"
        ordering = ['registry__name', 'name']
        unique_together = [['registry', 'name']]
        indexes = [
            models.Index(fields=['registry', 'name']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        registry_name = self.registry.name if self.registry else 'Без реестра'
        return f"{registry_name} | {self.name}"

    def get_all_parents(self):
        parents = []
        current = self.parent_group
        while current and not current.is_deleted:
            parents.append(current)
            current = current.parent_group
        return parents

    def get_all_children(self, visited=None):
        if visited is None:
            visited = set()

        if self.id in visited:
            return []

        visited.add(self.id)

        children = []
        for child in self.child_groups.filter(is_deleted=False):
            children.append(child)
            children.extend(child.get_all_children(visited.copy()))
        return children

    def get_all_users(self, visited=None):
        if visited is None:
            visited = set()

        if self.id in visited:
            return set()

        visited.add(self.id)

        users = list(self.users.filter(is_deleted=False))
        for child in self.child_groups.filter(is_deleted=False):
            users.extend(child.get_all_users(visited.copy()))

        seen = set()
        unique_users = []
        for user in users:
            if user.id not in seen:
                seen.add(user.id)
                unique_users.append(user)

        return unique_users

    def is_ancestor_of(self, group):
        current = group.parent_group
        while current:
            if current.id == self.id:
                return True
            current = current.parent_group
        return False


class AccessSection(models.Model):
    """Модель раздела доступа (второй уровень иерархии матрицы доступов)"""

    registry = models.ForeignKey(
        AccessRegistry,
        verbose_name="Реестр доступа",
        related_name='sections',
        on_delete=models.PROTECT,
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=64
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True
    )

    is_deleted = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = "Раздел доступа"
        verbose_name_plural = "Разделы доступа"
        ordering = ['registry', 'name']
        unique_together = [['registry', 'name']]

    def __str__(self):
        return f"{self.registry.name} | {self.name}"


class AccessNode(models.Model):
    """Модель узла доступа (третий уровень иерархии матрицы доступов)"""

    section = models.ForeignKey(
        AccessSection,
        verbose_name="Раздел доступа",
        related_name='nodes',
        on_delete=models.PROTECT
    )
    name = models.CharField(
        verbose_name="Доменное имя",
        max_length=128
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True
    )
    ip = models.GenericIPAddressField(
        verbose_name="IP-адрес",
        blank=True,
        null=True
    )

    is_deleted = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = "Узел доступа"
        verbose_name_plural = "Узлы доступа"
        ordering = ['section', 'name']
        unique_together = [['section', 'name']]

    def __str__(self):
        return f"{self.section.name} | {self.name}"


class AccessObject(models.Model):
    """Модель объекта доступа (четвёртый уровень иерархии матрицы доступов)"""

    node = models.ForeignKey(
        AccessNode,
        verbose_name="Раздел доступа",
        related_name='objects',
        on_delete=models.PROTECT
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=64
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True
    )
    resource_path = models.CharField(
        verbose_name="Путь к ресурсу",
        max_length=256
    )

    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Объект доступа"
        verbose_name_plural = "Объекты доступа"
        ordering = ['node', 'name']
        unique_together = [['node', 'name']]

    def __str__(self):
        return f"{self.node.name} | {self.name}"


class AccessType(models.Model):
    """Модель типа доступа (пятый уровень иерархии матрицы доступов)"""

    object = models.ForeignKey(
        AccessObject,
        verbose_name="Раздел доступа",
        related_name='types',
        on_delete=models.PROTECT
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=64
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True
    )

    is_deleted = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = "Тип доступа"
        verbose_name_plural = "Тип доступа"
        ordering = ['object', 'name']
        unique_together = [['object', 'name']]

    def __str__(self):
        return f"{self.object.node.name} | {self.object.name} | {self.name}"
