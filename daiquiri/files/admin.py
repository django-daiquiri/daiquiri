from django.contrib import admin

from .models import Directory


class DirectoryAdmin(admin.ModelAdmin):
    search_fields = ('path', )
    list_display = ('path', )
    list_display_links = ('path', )


admin.site.register(Directory, DirectoryAdmin)
