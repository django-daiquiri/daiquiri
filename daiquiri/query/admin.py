from django.contrib import admin

from daiquiri.jobs.admin import JobAdmin

from .models import QueryJob, DownloadJob, QueryArchiveJob, Example


class QueryJobAdmin(JobAdmin):
    search_fields = JobAdmin.search_fields + ['schema_name', 'table_name']
    list_display = JobAdmin.list_display + ['schema_name', 'table_name', 'nrows']
    actions = ['abort_job', 'archive_job']


class DownloadJobAdmin(JobAdmin):
    search_fields = JobAdmin.search_fields + ['schema_name', 'job__table_name', 'format_key']
    list_display = JobAdmin.list_display + ['job', 'file_path']
    actions = ['abort_job', 'archive_job']


class QueryArchiveJobAdmin(JobAdmin):
    search_fields = JobAdmin.search_fields + ['schema_name', 'job__table_name', 'format_key']
    list_display = JobAdmin.list_display + ['job', 'file_path']
    actions = ['abort_job', 'archive_job']


class ExampleAdmin(admin.ModelAdmin):
    search_fields = ('name', 'query_string')
    list_display = ('order', 'name', 'query_string')
    list_display_links = ('name', )


admin.site.register(QueryJob, QueryJobAdmin)
admin.site.register(DownloadJob, DownloadJobAdmin)
admin.site.register(QueryArchiveJob, QueryArchiveJobAdmin)
admin.site.register(Example, ExampleAdmin)
