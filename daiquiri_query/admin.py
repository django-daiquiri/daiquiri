from django.contrib import admin

from .models import QueryJob


class QueryJobAdmin(admin.ModelAdmin):
    pass

admin.site.register(QueryJob, QueryJobAdmin)
