from django.db import models


class Schema(models.Model):
    schema_name = models.CharField(max_length=256)
    utype = models.CharField(max_length=256, null=True, blank=True)  # noqa: DJ001
    description = models.CharField(max_length=256, null=True, blank=True)  # noqa: DJ001

    class Meta:
        db_table = 'schemas'

    def __str__(self):
        return self.schema_name


class Table(models.Model):
    schema = models.ForeignKey(Schema, related_name='tables', on_delete=models.CASCADE)

    schema_name = models.CharField(max_length=256)
    table_name = models.CharField(max_length=256)
    table_type = models.CharField(max_length=256)
    utype = models.CharField(max_length=256, null=True, blank=True)  # noqa: DJ001
    description = models.CharField(max_length=256, null=True, blank=True)  # noqa: DJ001
    table_index = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'tables'

    def __str__(self):
        return f'{self.schema_name}.{self.table_name}'


class Column(models.Model):
    table = models.ForeignKey(Table, related_name='columns', on_delete=models.CASCADE)

    table_name = models.CharField(max_length=256)
    column_name = models.CharField(max_length=256)
    datatype = models.CharField(max_length=256)
    arraysize = models.CharField(max_length=256, null=True, blank=True)  # noqa: DJ001
    size = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)  # noqa: DJ001
    utype = models.CharField(max_length=256, null=True, blank=True)  # noqa: DJ001
    unit = models.CharField(max_length=256, null=True, blank=True)  # noqa: DJ001
    ucd = models.CharField(max_length=256, null=True, blank=True)  # noqa: DJ001
    principal = models.IntegerField(default=0)
    indexed = models.IntegerField(default=0)
    std = models.IntegerField(default=0)
    column_index = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'columns'

    def __str__(self):
        return f'{self.table_name}.{self.column_name}'


class Key(models.Model):
    key_id = models.CharField(max_length=256, primary_key=True)
    from_table = models.CharField(max_length=256)
    target_table = models.CharField(max_length=256)
    description = models.CharField(max_length=256, null=True, blank=True)  # noqa: DJ001
    utype = models.CharField(max_length=256, null=True, blank=True)  # noqa: DJ001

    class Meta:
        db_table = 'keys'

    def __str__(self):
        return f'{self.key_id}: from {self.from_table} to {self.target_table}'


class KeyColumn(models.Model):
    id = models.AutoField(primary_key=True)
    key_id = models.CharField(max_length=256)
    from_column = models.CharField(max_length=256)
    target_column = models.CharField(max_length=256)

    class Meta:
        db_table = 'key_columns'

    def __str__(self):
        return f'{self.key_id}: from {self.from_column} to {self.target_column}'
