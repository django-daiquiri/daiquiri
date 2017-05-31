from django.db import models


class DatabasePermissionsManager(models.Manager):

    def get(self, user, database=None, database_name=None):
        queryset = self.get_queryset().filter(groups__in=user.groups.all())

        try:
            if database:
                return queryset.get(id=database.id)
            else:
                return queryset.get(name=database_name)
        except self.model.DoesNotExist:
            return False


class TablePermissionsManager(models.Manager):

    def get(self, user, database=None, database_name=None, table=None, table_name=None):
        queryset = self.get_queryset().filter(groups__in=user.groups.all())

        try:
            if table:
                return queryset.get(id=table.id)
            else:
                if database:
                    return queryset.filter(database=database).get(name=table_name)
                else:
                    return queryset.filter(database__name=database_name).get(name=table_name)
        except self.model.DoesNotExist:
            return False


class ColumnPermissionsManager(models.Manager):

    def get(self, user, database=None, database_name=None, table=None, table_name=None, column=None, column_name=None):
        queryset = self.get_queryset().filter(groups__in=user.groups.all())

        try:
            if column:
                return queryset.get(id=column.id)
            else:
                if table:
                    return queryset.filter(table=table).get(name=column_name)
                else:
                    if database:
                        return queryset.filter(table__database=database).filter(table__name=table_name).get(name=column_name)
                    else:
                        return queryset.filter(table__database__name=database_name).filter(table__name=table_name).get(name=column_name)
        except self.model.DoesNotExist:
            return False

    def all(self, user, database=None, database_name=None, table=None, table_name=None):
        queryset = self.get_queryset().filter(groups__in=user.groups.all())

        if table:
            return queryset.filter(table=table)
        else:
            if database:
                return queryset.filter(table__database=database).filter(table__name=table_name)
            else:
                return queryset.filter(table__database__name=database_name).filter(table__name=table_name)


class FunctionPermissionsManager(models.Manager):

    def get(self, user, function=None, function_name=None):
        queryset = self.get_queryset().filter(groups__in=user.groups.all())

        try:
            if function:
                return queryset.get(id=function.id)
            else:
                return queryset.get(name=function_name)
        except self.model.DoesNotExist:
            return False
