from django.db import models

from users.models import User

NULLABLE = {'blank': True, 'null': True}


class EmailAccount(models.Model):
    email = models.EmailField(unique=True, verbose_name='Почта')
    password = models.CharField(max_length=255, verbose_name='Пароль')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Учетная_запись_электронной_почты'
        verbose_name_plural = 'Учетные_записи_электронных_почт'


class EmailMessage(models.Model):
    email_id = models.IntegerField(default=True, verbose_name='Идентификатор')
    subject = models.CharField(max_length=255, verbose_name='Тема')
    date_email = models.CharField(max_length=200, default=None, blank=True, verbose_name='Дата')
    from_email = models.CharField(max_length=200, default=None, blank=True)
    type = models.CharField(max_length=200, default=None, **NULLABLE, verbose_name='Тип')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, verbose_name='Пользователь')
    body = models.TextField(default=None, **NULLABLE)
    attachments = models.TextField(default=None, **NULLABLE, verbose_name='Вложения')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение_электронной_почты'
        verbose_name_plural = 'Сообщении_электронных_почт'


class Title(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Заголовок'
        verbose_name_plural = 'Заголовки'
