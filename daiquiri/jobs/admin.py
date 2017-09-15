from django.contrib import admin

from .models import Job


class JobAdmin(admin.ModelAdmin):
    search_fields = ('id', 'job_type', 'owner__username', 'phase')
    list_display = ('id', 'job_type', 'owner', 'phase', 'creation_time')

admin.site.register(Job, JobAdmin)
