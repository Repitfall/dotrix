from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    login = models.CharField(
        verbose_name="Логин", max_length=64, unique=True)
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=32)
    first_name = models.CharField(
        verbose_name="Имя", max_length=32)
    patronymic = models.CharField(
        verbose_name="Отчество", max_length=32)
    post = models.CharField(
        verbose_name="Должность", max_length=128)
    created_at = models.DateTimeField(
        verbose_name="Дата создания", auto_now_add=True)

    auth_offline = models.BooleanField(
        verbose_name="Автономная авторизация")

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.last_name
