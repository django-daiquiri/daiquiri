from django.contrib import admin

from .models import Database, Table, Column, Function


class DatabaseAdmin(admin.ModelAdmin):
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


class FunctionAdmin(admin.ModelAdmin):
    search_fields = ('name', 'query_string')
    list_display = ('order', 'name', 'query_string')
    list_display_links = ('name', )


admin.site.register(Database, DatabaseAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(Column, ColumnAdmin)
admin.site.register(Function, FunctionAdmin)
