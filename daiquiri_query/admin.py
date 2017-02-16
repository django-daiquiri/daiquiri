from django.contrib import admin

from .models import QueryJob, Example


class QueryJobAdmin(admin.ModelAdmin):
    pass


class ExampleAdmin(admin.ModelAdmin):
    pass

admin.site.register(QueryJob, QueryJobAdmin)
admin.site.register(Example, ExampleAdmin)
