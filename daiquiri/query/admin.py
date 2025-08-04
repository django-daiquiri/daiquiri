from django.contrib import admin
from django.forms import ChoiceField, ModelForm

from daiquiri.jobs.admin import JobAdmin

from .models import DownloadJob, Example, QueryArchiveJob, QueryJob
from .utils import get_query_download_format_choices, get_query_language_choices, get_queue_choices


class QueryJobForm(ModelForm):
    queue = ChoiceField(choices=get_queue_choices())
    query_language = ChoiceField(choices=get_query_language_choices())


class DownloadJobForm(ModelForm):
    format_key = ChoiceField(choices=get_query_download_format_choices())


class ExampleForm(ModelForm):
    query_language = ChoiceField(choices=get_query_language_choices())


@admin.register(QueryJob)
class QueryJobAdmin(JobAdmin):
    form = QueryJobForm

    search_fields = [*JobAdmin.search_fields, 'schema_name', 'table_name']
    list_display = [*JobAdmin.list_display, 'schema_name', 'table_name', 'nrows']
    list_filter = [*JobAdmin.list_filter, 'query_language', 'queue']
    actions = ['abort_job', 'archive_job']


@admin.register(DownloadJob)
class DownloadJobAdmin(JobAdmin):
    form = DownloadJobForm

    search_fields = [*JobAdmin.search_fields, 'query_job__schema_name', 'query_job__table_name', 'format_key']
    list_display = [*JobAdmin.list_display, 'query_job', 'file_path']
    list_filter = [*JobAdmin.list_filter, 'format_key']
    raw_id_fields = ('query_job', )
    actions = ['abort_job', 'archive_job']


@admin.register(QueryArchiveJob)
class QueryArchiveJobAdmin(JobAdmin):
    search_fields = [*JobAdmin.search_fields, 'query_job__schema_name', 'query_job__table_name', 'column_name', 'files']
    list_display = [*JobAdmin.list_display, 'query_job', 'file_path']
    raw_id_fields = ('query_job', )
    actions = ['abort_job', 'archive_job']


@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    form = ExampleForm

    search_fields = ('name', 'query_string')
    list_display = ('order', 'name', 'query_string')
    list_display_links = ('name', )
    list_filter = ('query_language', )
