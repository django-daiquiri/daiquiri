from django.contrib import admin

from .models import ContactMessage


class ContactMessageAdmin(admin.ModelAdmin):
    search_fields = ("subject", "email", "author", "status", "user__username")
    list_display = ("subject", "email", "author", "status")


admin.site.register(ContactMessage, ContactMessageAdmin)
