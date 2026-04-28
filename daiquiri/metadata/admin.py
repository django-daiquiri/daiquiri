from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from daiquiri.core.validators import DatabaseObjectNameValidator

from .models import Column, Function, Schema, Table


class SchemaAdminForm(forms.ModelForm):
    name = forms.CharField(
        validators=[DatabaseObjectNameValidator()])
    license = forms.ChoiceField(choices=settings.LICENSE_CHOICES, required=False)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        instance = self.instance

        queryset = Schema.objects.filter(name__iexact=name)

        if instance and instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                _('Schema with this Name already exists.')
            )

        return name

class TableAdminForm(forms.ModelForm):
    name = forms.CharField(
        validators=[DatabaseObjectNameValidator()])
    license = forms.ChoiceField(choices=settings.LICENSE_CHOICES, required=False)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        schema = self.cleaned_data.get('schema')
        instance = self.instance

        queryset = Table.objects.filter(schema=schema, name__iexact=name)

        if instance and instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                _('This table already exists in this schema.')
            )

        return name

class ColumnAdminForm(forms.ModelForm):
    name = forms.CharField(validators=[DatabaseObjectNameValidator()])

    def clean_name(self):
        name = self.cleaned_data.get('name')
        table = self.cleaned_data.get('table')
        instance = self.instance

        queryset = Column.objects.filter(table=table, name__iexact=name)

        if instance and instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                _('This column already exists in this table.')
            )

        return name

class FunctionAdminForm(forms.ModelForm):
    name = forms.CharField(validators=[DatabaseObjectNameValidator()])

    def clean_name(self):
        name = self.cleaned_data.get('name')
        instance = self.instance

        queryset = Function.objects.filter(name__iexact=name)

        if instance and instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                _('Function with this Name already exists.')
            )

        return name

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
    form = ColumnAdminForm

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
    form = FunctionAdminForm

    search_fields = ('name', 'query_string')
    list_display = ('order', 'name', 'query_string')
    list_display_links = ('name', )


admin.site.register(Schema, SchemaAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(Column, ColumnAdmin)
admin.site.register(Function, FunctionAdmin)
