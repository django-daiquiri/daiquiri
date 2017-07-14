from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from daiquiri.core.adapter import get_adapter
from daiquiri.jobs.models import Job
from daiquiri.metadata.models import Database, Table, Column, Function
from daiquiri.uws.settings import PHASE_QUEUED

from daiquiri.query.tasks import submit_query

from .utils import get_user_database_name
from .exceptions import TableError, ADQLSyntaxError, MySQLSyntaxError, PermissionError

from queryparser.mysql import MySQLQueryProcessor
from queryparser.adql import ADQLQueryTranslator


class QueryJobQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        # drop tables for all deleted jobs
        for job in self.all():
            job.drop_table()

        return super(QueryJobQuerySet, self).delete(*args, **kwargs)


class QueryJobManager(models.Manager):

    def get_queryset(self):
        return QueryJobQuerySet(self.model, using=self._db)

    def filter_by_owner(self, user):
        if user.is_anonymous():
            return self.get_queryset().filter(owner=None)
        else:
            return self.get_queryset().filter(owner=user)

    def submit(self, query_language, query, queue, table_name, user, sync=False):
        """
        Submit a query to the job management and the query backend.
        """

        # check if a table with that name already exists
        errors = self._check_table(table_name)
        if errors:
            raise TableError(errors)

        # translate adql -> mysql string
        if query_language == 'adql':
            try:
                adt = ADQLQueryTranslator(query)
                actual_query = adt.to_mysql()
            except RuntimeError as e:
                raise ADQLSyntaxError(str(e))
        else:
            actual_query = query.strip(';')

        # parse the query
        qp = MySQLQueryProcessor(actual_query)
        qp.process_query()

        # check for syntax errors
        if qp.syntax_errors:
            raise MySQLSyntaxError(qp.syntax_errors)

        # check permissions on keywords, databases, tables, columns, and functions
        errors = self._check_permissions(user, qp)
        if errors:
            raise PermissionError(errors)

        # store statistics/meta information
        # todo

        job = self.model(
            query_language=query_language,
            query=query,
            actual_query=actual_query,
            owner=user if not user.is_anonymous() else None,
            database_name=get_user_database_name(user),
            table_name=table_name,
            queue=queue,
            phase=PHASE_QUEUED,
            creation_time=now(),
            job_type=Job.JOB_TYPE_QUERY
        )
        job.save()

        # start the submit_query task in a syncronous or asuncronous way
        job_id = str(job.id)
        if not settings.ASYNC or sync:
            submit_query.apply((job_id, ), task_id=job_id)
        else:
            submit_query.apply_async((job_id, ), task_id=job_id, queue=job.queue)

        return job.id

    def _check_table(self, table_name):
        # check if a job with this table name exists
        try:
            self.get(table_name=table_name)
            return [_('A job with this table name aready exists.')]

        except self.model.DoesNotExist:
            # check if the table alread exists in the database
            pass

    def _check_permissions(self, user, qp):
        errors = []

        # check keywords against whitelist
        for keywords in qp.keywords:
            pass

        # check permissions on databases/tables/columns
        for column in qp.columns:
            try:
                database_name, table_name, column_name = column.split('.')

                # check permission on database
                try:
                    database = Database.objects.filter_by_access_level(user).get(name=database_name)
                except Database.DoesNotExist:
                    errors.append(_('Database %s not found.') % database_name)
                    continue

                # check permission on table
                try:
                    table = Table.objects.filter_by_access_level(user).filter(database=database).get(name=table_name)
                except Table.DoesNotExist:
                    errors.append(_('Table %s not found.') % table_name)
                    continue

                # check permission on column
                try:
                    column = Column.objects.filter_by_access_level(user).filter(table=table).get(name=column_name)
                except Column.DoesNotExist:
                    errors.append(_('Column %s not found.') % column_name)
                    continue

            except ValueError:
                errors.append(_('No database given for column %s') % column)

        # check permissions on functions
        for function_name in qp.functions:
            if function_name.upper() in get_adapter('data').functions:
                continue
            else:
                # check permission on function
                function = Function.objects.filter_by_access_level(user).get(name=function_name)
                if not function:
                    errors.append(_('Function %s not found.') % function_name)
                    continue

        # return the error stack
        return list(set(errors))
