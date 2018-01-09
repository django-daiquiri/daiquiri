from django.contrib import admin

from .models import Collection, ArchiveJob


class CollectionAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name', 'access_level')


class ArchiveJobAdmin(admin.ModelAdmin):
    search_fields = ('id', 'owner__username', 'phase', 'file_path')
    list_display = ('id', 'owner', 'phase', 'creation_time', 'file_path')


admin.site.register(Collection, CollectionAdmin)
admin.site.register(ArchiveJob, ArchiveJobAdmin)
