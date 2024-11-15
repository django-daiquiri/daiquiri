from django import forms
from django.conf import settings
from django.contrib import admin

from .models import Column, Function, Schema, Table


class SchemaAdminForm(forms.ModelForm):
    license = forms.ChoiceField(choices=settings.LICENSE_CHOICES, required=False)


class TableAdminForm(forms.ModelForm):
    license = forms.ChoiceField(choices=settings.LICENSE_CHOICES, required=False)


class SchemaAdmin(admin.ModelAdmin):
    form = SchemaAdminForm

    search_fields = ('name',)
    list_display = ('order', '__str__', 'access_level', 'metadata_access_level')
    list_display_links = ('__str__', )


class TableAdmin(admin.ModelAdmin):
    form = TableAdminForm

    search_fields = ('name', 'schema__name')
    list_display = ('order', '__str__', 'access_level', 'metadata_access_level')
    list_display_links = ('__str__', )


class ColumnAdmin(admin.ModelAdmin):
    search_fields = ('name', 'table__name', 'table__schema__name', 'datatype')
    list_display = ('order', '__str__', 'datatype', 'access_level', 'metadata_access_level')
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
