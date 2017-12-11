from django.contrib import admin

from .models import ArchiveJob


class ArchiveJobAdmin(admin.ModelAdmin):
    search_fields = ('id', 'owner__username', 'phase', 'file_path')
    list_display = ('id', 'owner', 'phase', 'creation_time', 'file_path')


admin.site.register(ArchiveJob, ArchiveJobAdmin)
