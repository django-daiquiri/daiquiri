from django.conf import settings
from django.contrib import admin

from .models import Schema, Table, Column, Function


class SchemaAdmin(admin.ModelAdmin):
    search_fields = ('__str__', )
    list_display = ('order' ,'__str__', 'access_level', 'metadata_access_level')
    list_display_links = ('__str__', )


class TableAdmin(admin.ModelAdmin):
    search_fields = ('__str__', )
    list_display = ('order' ,'__str__', 'access_level', 'metadata_access_level')
    list_display_links = ('__str__', )


class ColumnAdmin(admin.ModelAdmin):
    search_fields = ('__str__', 'datatype')
    list_display = ('order' ,'__str__', 'datatype', 'access_level', 'metadata_access_level')
    list_display_links = ('__str__', )

    # only show access_level, metadata_access_level, and groups when
    # settings.METADATA_COLUMN_PERMISSIONS is set
    if not settings.METADATA_COLUMN_PERMISSIONS:
        fields = (
            'table',
            'order',
            'name',
            'description',
            'unit',
            'ucd',
            'utype',
            'datatype',
            'arraysize',
            'principal',
            'indexed',
            'std'
        )


class FunctionAdmin(admin.ModelAdmin):
    search_fields = ('name', 'query_string')
    list_display = ('order', 'name', 'query_string')
    list_display_links = ('name', )


admin.site.register(Schema, SchemaAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(Column, ColumnAdmin)
admin.site.register(Function, FunctionAdmin)
