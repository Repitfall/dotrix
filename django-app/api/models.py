from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Модель пользователя"""

    username = models.CharField(
        verbose_name="Логин", max_length=64, unique=True)
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=32)
    first_name = models.CharField(
        verbose_name="Имя", max_length=32)
    patronymic = models.CharField(
        verbose_name="Отчество", max_length=32, blank=True)
    post = models.CharField(
        verbose_name="Должность", max_length=128)
    created_at = models.DateTimeField(
        verbose_name="Дата создания", auto_now_add=True)

    auth_offline = models.BooleanField(
        verbose_name="Автономная авторизация", default=True)

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.last_name


class AccessRegistry(models.Model):
    """Модель реестра доступа (первый уровень иерархии доступов)"""

    name = models.CharField(
        verbose_name="Название", max_length=64)
    description = models.TextField(
        verbose_name="Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Реестр доступа"
        verbose_name_plural = "Реестры доступа"
        ordering = ['name']

    def __str__(self):
        return self.name


class AccessSection(models.Model):
    """Модель раздела доступа (второй уровень иерархии матрицы доступов)"""

    registry = models.ForeignKey(
        verbose_name="Реестр доступа", to=AccessRegistry, related_name='sections', on_delete=models.SET_NULL, null=True)
    name = models.CharField(
        verbose_name="Название", max_length=64)
    description = models.TextField(
        verbose_name="Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Реестр доступа"
        verbose_name_plural = "Реестры доступа"
        ordering = ['registry', 'name']
        unique_together = [['registry', 'name']]

    def __str__(self):
        return f"{self.registry.name} | {self.name}"


class AccessNode(models.Model):
    """Модель узла доступа (третий уровень иерархии матрицы доступов)"""

    section = models.ForeignKey(
        verbose_name="Раздел доступа", to=AccessSection, related_name='nodes', on_delete=models.SET_NULL, null=True)
    name = models.CharField(
        verbose_name="Доменное имя", max_length=128)
    description = models.TextField(
        verbose_name="Описание", blank=True, null=True)
    ip = models.GenericIPAddressField(
        verbose_name="IP-адрес", blank=True, null=True)

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
        verbose_name="Раздел доступа", to=AccessNode, related_name='objects', on_delete=models.SET_NULL, null=True)
    name = models.CharField(
        verbose_name="Название", max_length=64)
    description = models.TextField(
        verbose_name="Описание", blank=True, null=True)
    resource_path = models.CharField(
        verbose_name="Путь к ресурсу", max_length=256)

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
        verbose_name="Раздел доступа", to=AccessObject, related_name='types', on_delete=models.SET_NULL, null=True)
    name = models.CharField(
        verbose_name="Название", max_length=64)
    description = models.TextField(
        verbose_name="Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Тип доступа"
        verbose_name_plural = "Тип доступа"
        ordering = ['object', 'name']
        unique_together = [['object', 'name']]

    def __str__(self):
        return f"{self.object.node.name} | {self.object.name} | {self.name}"
