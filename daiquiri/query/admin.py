from django.contrib import admin

from .models import QueryJob, DownloadJob, QueryArchiveJob, Example


class QueryJobAdmin(admin.ModelAdmin):
    search_fields = ('id', 'job_type', 'owner__username', 'phase', 'schema_name', 'table_name')
    list_display = ('id', 'job_type', 'owner', 'phase', 'creation_time', 'schema_name', 'table_name', 'nrows')


class DownloadJobAdmin(admin.ModelAdmin):
    search_fields = ('id', 'job_type', 'owner__username', 'phase', 'job__table_name', 'format_key')
    list_display = ('id', 'job_type', 'owner', 'phase', 'creation_time', 'job', 'file_path')


class QueryArchiveJobAdmin(admin.ModelAdmin):
    search_fields = ('id', 'job_type', 'owner__username', 'phase', 'job__table_name', 'format_key')
    list_display = ('id', 'job_type', 'owner', 'phase', 'creation_time', 'job', 'file_path')


class ExampleAdmin(admin.ModelAdmin):
    search_fields = ('name', 'query_string')
    list_display = ('order', 'name', 'query_string')
    list_display_links = ('name', )


admin.site.register(QueryJob, QueryJobAdmin)
admin.site.register(DownloadJob, DownloadJobAdmin)
admin.site.register(QueryArchiveJob, QueryArchiveJobAdmin)
admin.site.register(Example, ExampleAdmin)
