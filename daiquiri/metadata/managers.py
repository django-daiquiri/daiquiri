from django.db import models


class PermissionsManager(models.Manager):

    def get_queryset_for_user(self, user):
        if user.is_anonymous():
            return self.get_queryset().filter(metadata_access_level='PUBLIC')
        else:
            q = models.Q(metadata_access_level='PUBLIC') | \
                models.Q(metadata_access_level='INTERNAL') | \
                models.Q(groups__in=user.groups.all())
            return self.get_queryset().filter(q)


class DatabasePermissionsManager(PermissionsManager):

    def get(self, user, database=None, database_name=None):
        if database:
            return self.get_queryset_for_user(user).get(id=database.id)
        else:
            return self.get_queryset_for_user(user).get(name=database_name)

    def all(self, user):
        return self.get_queryset_for_user(user).all()


class TablePermissionsManager(PermissionsManager):

    def get(self, user, database=None, database_name=None, table=None, table_name=None):
        try:
            if table:
                return self.get_queryset_for_user(user).get(id=table.id)
            else:
                if database:
                    return self.get_queryset_for_user(user).filter(database=database).get(name=table_name)
                else:
                    return self.get_queryset_for_user(user).filter(database__name=database_name).get(name=table_name)
        except self.model.DoesNotExist:
            return False


class ColumnPermissionsManager(PermissionsManager):

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


class FunctionPermissionsManager(PermissionsManager):

    def get(self, user, function=None, function_name=None):
        queryset = self.get_queryset().filter(groups__in=user.groups.all())

        try:
            if function:
                return queryset.get(id=function.id)
            else:
                return queryset.get(name=function_name)
        except self.model.DoesNotExist:
            return False
