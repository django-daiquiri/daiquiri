from django.contrib import admin

from .models import Record


class RecordAdmin(admin.ModelAdmin):
    search_fields = ('resource', 'user__username')
    list_display = ('time', 'resource_type', 'client_ip', 'user')
    list_display_links = ('time', )


admin.site.register(Record, RecordAdmin)
