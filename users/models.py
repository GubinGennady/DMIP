from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'blank': True, 'null': True}


class User(AbstractUser):
    username = models.CharField(max_length=200, unique=True, default=None, verbose_name='Логин')
    password = models.CharField(max_length=200, verbose_name='Пароль')
    is_active = models.BooleanField(default=False, verbose_name='Активен')

    login_gmail = models.CharField(max_length=200, default=None, **NULLABLE, verbose_name='Логин_gmail')
    password_gmail = models.CharField(max_length=200, default=None, **NULLABLE, verbose_name='Пароль_gmail')

    login_mail = models.CharField(max_length=200, default=None, **NULLABLE, verbose_name='Логин_mail')
    password_mail = models.CharField(max_length=200, default=None, **NULLABLE, verbose_name='Пароль_mail')

    login_yandex = models.CharField(max_length=200, default=None, **NULLABLE, verbose_name='Логин_yandex')
    password_yandex = models.CharField(max_length=200, default=None, **NULLABLE, verbose_name='Пароль_yandex')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
