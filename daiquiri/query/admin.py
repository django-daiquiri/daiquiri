from django.contrib import admin

from .models import QueryJob, Example


class QueryJobAdmin(admin.ModelAdmin):
    search_fields = ('id', 'job_type', 'owner__username', 'phase', 'database_name', 'table_name')
    list_display = ('id', 'job_type', 'owner', 'phase', 'creation_time', 'database_name', 'table_name', 'nrows')


class ExampleAdmin(admin.ModelAdmin):
    search_fields = ('name', 'query_string')
    list_display = ('order', 'name', 'query_string')
    list_display_links = ('name', )


admin.site.register(QueryJob, QueryJobAdmin)
admin.site.register(Example, ExampleAdmin)
