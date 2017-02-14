from django.db import models, ProgrammingError
from django.contrib.auth.models import Group
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from daiquiri_core.adapter import get_adapter

from .managers import (
    DatabasePermissionsManager,
    TablePermissionsManager,
    ColumnPermissionsManager,
    FunctionPermissionsManager
)


@python_2_unicode_compatible
class Database(models.Model):

    objects = models.Manager()
    permissions = DatabasePermissionsManager()

    order = models.IntegerField(null=True, blank=True)

    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)

    utype = models.CharField(max_length=256, null=True, blank=True)

    groups = models.ManyToManyField(Group, blank=True)

    class Meta:
        ordering = ('order', )

        verbose_name = _('Database')
        verbose_name_plural = _('Databases')

        permissions = (('view_database', 'Can view Database'),)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Table(models.Model):

    TYPE_TABLE = 'table'
    TYPE_VIEW = 'view'
    TYPE_CHOICES = (
        (TYPE_TABLE, _('Table')),
        (TYPE_VIEW, _('View'))
    )

    objects = models.Manager()
    permissions = TablePermissionsManager()

    database = models.ForeignKey(Database, related_name='tables')

    order = models.IntegerField(null=True, blank=True)

    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)

    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    utype = models.CharField(max_length=256, null=True, blank=True)

    groups = models.ManyToManyField(Group, blank=True)

    class Meta:
        ordering = ('database__order', 'order', )

        verbose_name = _('Table')
        verbose_name_plural = _('Tables')

        permissions = (('view_table', 'Can view Table'),)

    def __str__(self):
        return self.database.name + '.' + self.name

    def save(self, *args, **kwargs):
        super(Table, self).save(*args, **kwargs)

        try:
            get_adapter('metadata').store_table_metadata(self.database.name, self.name, {
                'order': self.order,
                'name': self.name,
                'description': self.description,
                'type': self.type,
                'utype': self.utype
            })
        except ProgrammingError:
            pass


@python_2_unicode_compatible
class Column(models.Model):

    objects = models.Manager()
    permissions = ColumnPermissionsManager()

    table = models.ForeignKey(Table, related_name='columns')

    order = models.IntegerField(null=True, blank=True)

    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)

    unit = models.CharField(max_length=256, null=True, blank=True)
    ucd = models.CharField(max_length=256, null=True, blank=True)
    utype = models.CharField(max_length=256, null=True, blank=True)

    datatype = models.CharField(max_length=256, null=True, blank=True)
    size = models.IntegerField(null=True, blank=True, help_text=_('The length of variable length datatypes, e.g. varchar(256).'))

    principal = models.BooleanField(default=False, help_text=_('This column is considered a core part of the content.'))
    indexed = models.BooleanField(default=False, help_text=_('This column is indexed.'))
    std = models.BooleanField(default=False, help_text=_('This column is defined by some standard.'))

    groups = models.ManyToManyField(Group, blank=True)

    class Meta:
        ordering = ('table__database__order', 'table__order', 'order', )

        verbose_name = _('Column')
        verbose_name_plural = _('Columns')

        permissions = (('view_column', 'Can view Column'),)

    def __str__(self):
        return self.table.database.name + '.' + self.table.name + '.' + self.name

    def save(self, *args, **kwargs):
        super(Column, self).save(*args, **kwargs)

        try:
            get_adapter('metadata').store_column_metadata(self.table.database.name, self.table.name, self.name, {
                'order': self.order,
                'name': self.name,
                'description': self.description,
                'unit': self.unit,
                'ucd': self.ucd,
                'utype': self.utype,
                'datatype': self.datatype,
                'size': self.size,
                'principal': self.principal,
                'indexed': self.indexed,
                'std': self.std
            })
        except ProgrammingError:
            pass


@python_2_unicode_compatible
class Function(models.Model):

    objects = models.Manager()
    permissions = FunctionPermissionsManager()

    order = models.IntegerField(null=True, blank=True)

    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)

    groups = models.ManyToManyField(Group, blank=True)

    class Meta:
        ordering = ('order', )

        verbose_name = _('Function')
        verbose_name_plural = _('Functions')

        permissions = (('view_function', 'Can view Function'),)

    def __str__(self):
        return self.name
