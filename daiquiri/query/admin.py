from django.contrib import admin

from .models import QueryJob, Example


class QueryJobAdmin(admin.ModelAdmin):
    pass


class ExampleAdmin(admin.ModelAdmin):
    search_fields = ("name", "description", "query_string")
    list_display = ("id", "order", "name", "description", "query_string")


admin.site.register(QueryJob, QueryJobAdmin)
admin.site.register(Example, ExampleAdmin)
