from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Job


class JobAdmin(admin.ModelAdmin):
    search_fields = ['id', 'job_type', 'owner__username', 'phase']
    list_display = ['id', 'job_type', 'owner', 'run_id', 'phase', 'creation_time']

    list_filter = ['job_type', 'phase']
    ordering = ['-creation_time']

    def abort_job(self, request, queryset):
        for job in queryset:
            try:
                job.abort()
            except NotImplementedError:
                pass

    def archive_job(self, request, queryset):
        for job in queryset:
            try:
                job.archive()
            except NotImplementedError:
                pass

    abort_job.short_description = _('Abort selected jobs')
    archive_job.short_description = _('Archive selected jobs')


admin.site.register(Job, JobAdmin)
