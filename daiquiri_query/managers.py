from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from daiquiri_jobs.models import Job
from daiquiri_metadata.models import Database, Table, Column, Function
from daiquiri_uws.settings import PHASE_PENDING

from .exceptions import *

from queryparser.mysql import MySQLQueryProcessor


class QueryJobsSubmissionManager(models.Manager):

    def submit(self, query, user, tablename=None, queue=None):

        tablename = self._get_tablename(tablename)
        queue = self._get_queue(queue)

        # check sanity (table exists etc.)

        # translate adql -> mysql string

        # parse the query
        qp = MySQLQueryProcessor(query)
        qp.process_query()

        # check for syntax errors
        if qp.syntax_errors:
            raise MySQLSyntaxError(qp.syntax_errors)

        # check permissions on keywords, databases, tables, columns, and functions
        errors = self._check_permissions(user, qp)
        if errors:
            raise PermissionError(errors)

        # store statistics/meta information

        job = self.model(
            query=query,
            owner=user,
            tablename=tablename,
            queue=queue,
            phase=PHASE_PENDING,
            job_type=Job.JOB_TYPE_QUERY
        )
        job.save()

        # create actual query

    def _get_tablename(self, tablename):
        if tablename:
            return tablename
        else:
            return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    def _get_queue(self, queue):
        if queue:
            return queue
        else:
            return 'default'

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
                    database = Database.objects.get(name=database_name, groups__in=user.groups.all())
                except Database.DoesNotExist:
                    errors.append(_('Database %s not found.') % database_name)
                    continue

                # check permission on table
                try:
                    table = Table.objects.get(name=table_name, database=database, groups__in=user.groups.all())
                except Table.DoesNotExist:
                    errors.append(_('Table %s.%s not found.') % (database_name, table_name))
                    continue

                # check permission on column
                try:
                    Column.objects.get(name=column_name, table=table, groups__in=user.groups.all())
                except Column.DoesNotExist:
                    errors.append(_('Column %s.%s.%s not found.') % (database_name, table_name, column_name))
                    continue

            except ValueError:
                errors.append(_('No database given for column %s') % column)

        # check permissions on functions
        for function in qp.functions:
            # check permission on function
            try:
                Function.objects.get(name=function_name, groups__in=user.groups.all())
            except Function.DoesNotExist:
                errors.append(_('Function %s not found.') % function)
                continue

        # return the error stack
        return errors
