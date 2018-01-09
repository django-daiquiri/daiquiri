from django.contrib import admin

from .models import Directory


class DirectoryAdmin(admin.ModelAdmin):
    search_fields = ('path', 'access_level')
    list_display = ('absolute_path', 'path' , 'depth', 'access_level')
    list_display_links = ('absolute_path', )
    readonly_fields = ('depth', )

admin.site.register(Directory, DirectoryAdmin)
