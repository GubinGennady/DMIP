from django.contrib import admin
from .models import Title, EmailMessage

# Register your models here.
admin.site.register(Title)


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('type', 'email_id', 'subject',)
