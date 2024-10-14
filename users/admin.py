from django.contrib import admin

from users.models import User


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('login_yandex', 'password_yandex',
                    'login_gmail', 'password_gmail',
                    'login_mail', 'password_mail')
