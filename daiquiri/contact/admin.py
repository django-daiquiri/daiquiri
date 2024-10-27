from django import forms
from django.contrib import admin

from .models import AnnouncementMessage, ContactMessage, MessageFilter


class AnnouncementMessageAdminForm(forms.ModelForm):
    visibility_filter = forms.ChoiceField(choices=MessageFilter().CHOICES)


@admin.action(description="Make selected messages visible")
def make_visible(modeladmin, request, queryset):
    queryset.update(visible=True)


@admin.action(description="Make selected messages invisible")
def make_invisible(modeladmin, request, queryset):
    queryset.update(visible=False)


class ContactMessageAdmin(admin.ModelAdmin):
    search_fields = ("subject", "email", "author", "status", "user__username")
    list_display = ("subject", "email", "author", "status")


class AnnouncementMessageAdmin(admin.ModelAdmin):
    form = AnnouncementMessageAdminForm

    search_fields = ("title", "announcement")
    list_display = ("title", "visible", "announcement", "announcement_type", "updated")
    actions = [make_visible, make_invisible]

admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(AnnouncementMessage, AnnouncementMessageAdmin)
