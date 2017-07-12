from django.db import models, ProgrammingError
from django.contrib.auth.models import Group
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.adapter import get_adapter

from .managers import (
    DatabasePermissionsManager,
    TablePermissionsManager,
    ColumnPermissionsManager,
    FunctionPermissionsManager
)

LICENSE_CC0 = 'CC0'
LICENSE_PD = 'PD'
LICENSE_BY = 'BY'
LICENSE_BY_SA = 'BY_SA'
LICENSE_BY_ND = 'BY_ND'
LICENSE_BY_NC = 'BY_NC'
LICENSE_BY_NC_SA = 'BY_NC_SA'
LICENSE_BY_NC_ND = 'BY_NC_ND'
LICENSE_CHOICES = (
    (LICENSE_CC0, 'CC0 1.0 Universal (CC0 1.0)'),
    (LICENSE_PD, 'Public Domain Mark'),
    (LICENSE_BY, 'Attribution 4.0 International (CC BY 4.0)'),
    (LICENSE_BY_SA, 'Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)'),
    (LICENSE_BY_ND, 'Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)'),
    (LICENSE_BY_NC, 'Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)'),
    (LICENSE_BY_NC_SA, 'Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)'),
    (LICENSE_BY_NC_ND, 'Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)')
)

LICENSE_URLS = {
    LICENSE_CC0: 'https://creativecommons.org/publicdomain/zero/1.0/',
    LICENSE_PD: None,
    LICENSE_BY: 'https://creativecommons.org/licenses/by/4.0/',
    LICENSE_BY_SA: 'https://creativecommons.org/licenses/by-sa/4.0/',
    LICENSE_BY_ND: 'https://creativecommons.org/licenses/by-nd/4.0/',
    LICENSE_BY_NC: 'https://creativecommons.org/licenses/by-nc/4.0/',
    LICENSE_BY_NC_SA: 'https://creativecommons.org/licenses/by-nc-sa/4.0/',
    LICENSE_BY_NC_ND: 'https://creativecommons.org/licenses/by-nc-nd/4.0/'
}

ACCESS_LEVEL_PRIVATE = 'PRIVATE'
ACCESS_LEVEL_INTERNAL = 'INTERNAL'
ACCESS_LEVEL_PUBLIC = 'PUBLIC'
ACCESS_LEVEL_CHOICES = (
    (ACCESS_LEVEL_PRIVATE, _('Private - access must be granted by group')),
    (ACCESS_LEVEL_INTERNAL, _('Internal - logged in users can access')),
    (ACCESS_LEVEL_PUBLIC, _('Public - anonymous visitors can access'))
)

@python_2_unicode_compatible
class Database(models.Model):

    objects = models.Manager()
    permissions = DatabasePermissionsManager()

    order = models.IntegerField(
        default=0, null=True, blank=True,
        verbose_name=_('Order'),
        help_text=_('Position in lists.')
    )
    name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
        help_text=_('Name of the database on the database server.')
    )
    title = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Title'),
        help_text=_('Human readable title of the database.')
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_('Description'),
        help_text=_('A brief description of the database to be displayed in the user interface.')
    )
    long_description = models.TextField(
        null=True, blank=True,
        verbose_name=_('Long description'),
        help_text=_('A more extensive description of the database to be displayed on the public database page.')
    )
    attribution = models.TextField(
        null=True, blank=True,
        verbose_name=_('Attribution'),
        help_text=_('The desired attribution for the database.')
    )
    license = models.CharField(
        max_length=8, choices=LICENSE_CHOICES, null=True, blank=True,
        verbose_name=_('License')
    )
    pid = models.URLField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Persistent identifier'),
    )
    utype = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('IVOA Utype'),
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Access level')
    )
    metadata_access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Metadata access level')
    )
    groups = models.ManyToManyField(
        Group, blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to the database.')
    )

    class Meta:
        ordering = ('order', )

        verbose_name = _('Database')
        verbose_name_plural = _('Databases')

        permissions = (('view_database', 'Can view Database'),)

    def __str__(self):
        return self.name

    @property
    def query_string(self):
        return get_adapter('data').escape_identifier(self.name)

    @property
    def license_label(self):
        return dict(LICENSE_CHOICES)[self.license]

    @property
    def license_url(self):
        return LICENSE_URLS[self.license]


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

    database = models.ForeignKey(
        Database, related_name='tables',
        verbose_name=_('Database'),
        help_text=_('Database the table belongs to.')
    )
    order = models.IntegerField(
        null=True, blank=True,
        verbose_name=_('Order'),
        help_text=_('Position in lists.')
    )
    name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
        help_text=_('Identifier of the table on the database server.')
    )
    title = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Title'),
        help_text=_('Human readable title of the table.')
    )
    description = models.TextField(null=True, blank=True,
        verbose_name=_('Description'),
        help_text=_('A brief description of the table to be displayed in the user interface.')
    )
    long_description = models.TextField(
        null=True, blank=True,
        verbose_name=_('Long description'),
        help_text=_('A more extensive description of the table to be displayed on the public database page.')
    )
    attribution = models.TextField(
        null=True, blank=True,
        verbose_name=_('Attribution'),
        help_text=_('The desired attribution for the table.')
    )
    license = models.CharField(
        max_length=8, choices=LICENSE_CHOICES, null=True, blank=True,
        verbose_name=_('License')
    )
    pid = models.URLField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Persistent identifier')
    )
    type = models.CharField(
        max_length=8, choices=TYPE_CHOICES,
        verbose_name=_('Type of table')
    )
    utype = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('IVOA Utype')
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Access level')
    )
    metadata_access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Metadata access level')
    )
    groups = models.ManyToManyField(
        Group, blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to the table.')
    )

    class Meta:
        ordering = ('database__order', 'order', )

        verbose_name = _('Table')
        verbose_name_plural = _('Tables')

        permissions = (('view_table', 'Can view Table'),)

    def __str__(self):
        return self.database.name + '.' + self.name

    @property
    def query_string(self):
        adapter = get_adapter('data')
        return '%(database)s.%(table)s' % {
            'database': adapter.escape_identifier(self.database.name),
            'table': adapter.escape_identifier(self.name)
        }

    @property
    def license_label(self):
        return dict(LICENSE_CHOICES)[self.license]

    @property
    def license_url(self):
        return LICENSE_URLS[self.license]


@python_2_unicode_compatible
class Column(models.Model):

    objects = models.Manager()
    permissions = ColumnPermissionsManager()

    table = models.ForeignKey(
        Table, related_name='columns',
        help_text=_('Table the column belongs to.')
    )
    order = models.IntegerField(
        null=True, blank=True,
        verbose_name=_('Order'),
        help_text=_('Position in lists.')
    )
    name = models.CharField(max_length=256,
        verbose_name=_('Name'),
        help_text=_('Identifier of the column on the database server.')
    )
    description = models.TextField(null=True, blank=True,
        verbose_name=_('Description'),
        help_text=_('A brief description of the column to be displayed in the user interface.')
    )
    unit = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Unit')
    )
    ucd = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('IVOA UCDs')
    )
    utype = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('IVOA Utype')
    )
    datatype = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name=_('Datatype'),
        help_text=_('The datatype of the column on the database server.')
    )
    size = models.IntegerField(
        null=True, blank=True,
        verbose_name=_('Size'),
        help_text=_('The length of variable length datatypes, e.g. varchar(256).')
    )
    principal = models.BooleanField(
        default=False,
        verbose_name=_('Principal'),
        help_text=_('Designates whether the column is considered a core part of the content.')
    )
    indexed = models.BooleanField(
        default=False,
        verbose_name=_('Indexed'),
        help_text=_('Designates whether the column is indexed.')
    )
    std = models.BooleanField(
        default=False,
        verbose_name=_('Standard'),
        help_text=_('Designates whether the column is defined by some standard.')
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES, null=True, blank=True,
        verbose_name=_('Access level')
    )
    metadata_access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES, null=True, blank=True,
        verbose_name=_('Metadata access level')
    )
    groups = models.ManyToManyField(
        Group, blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to the column.')
    )

    class Meta:
        ordering = ('table__database__order', 'table__order', 'order', )

        verbose_name = _('Column')
        verbose_name_plural = _('Columns')

        permissions = (('view_column', 'Can view Column'),)

    def __str__(self):
        return self.table.database.name + '.' + self.table.name + '.' + self.name

    @property
    def query_string(self):
        return get_adapter('data').escape_identifier(self.name)


@python_2_unicode_compatible
class Function(models.Model):

    objects = models.Manager()
    permissions = FunctionPermissionsManager()

    order = models.IntegerField(
        null=True, blank=True,
        verbose_name=_('Order'),
        help_text=_('Position in lists.')
    )
    name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
        help_text=_('Identifier of the function on the server.')
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_('Description'),
        help_text=_('A brief description of the function to be displayed in the user interface.')
    )
    query_string = models.CharField(
        max_length=256,
        verbose_name=_('Query string'),
        help_text=_('Prototype of this function in a SQL query.')
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Access level')
    )
    metadata_access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Metadata access level')
    )
    groups = models.ManyToManyField(
        Group, blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to this function.')
    )

    class Meta:
        ordering = ('order', )

        verbose_name = _('Function')
        verbose_name_plural = _('Functions')

        permissions = (('view_function', 'Can view Function'),)

    def __str__(self):
        return self.name
