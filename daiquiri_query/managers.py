from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from daiquiri_jobs.models import Job
from daiquiri_metadata.models import Database, Table, Column, Function
from daiquiri_uws.settings import PHASE_PENDING

from .exceptions import *

from queryparser.mysql import MySQLQueryProcessor
from queryparser.adql import ADQLQueryTranslator


class QueryJobsSubmissionManager(models.Manager):

    def submit(self, data, user):

        query = data['query']
        query_language = data['query_language']
        tablename = self._get_tablename(data['tablename'])
        queue = self._get_queue(data['queue'])

        # check sanity (table exists etc.)
        # todo

        if query_language == 'adql':
            # translate adql -> mysql string
            try:
                adt = ADQLQueryTranslator(query)
                actual_query = adt.to_mysql()
            except RuntimeError as e:
                raise ADQLSyntaxError(str(e))
        else:
            actual_query = query

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
                database = Database.permissions.get(user, database_name=database_name)
                if not database:
                    errors.append(_('Database %s not found.') % database_name)
                    continue

                # check permission on table
                table = Table.permissions.get(user, database_name=database_name, table_name=table_name)
                if not table:
                    errors.append(_('Table %s not found.') % table_name)
                    continue

                # check permission on column
                column = Column.permissions.get(user, database_name=database_name, table_name=table_name, column_name=column_name)
                if not column:
                    errors.append(_('Column %s not found.') % column_name)
                    continue

            except ValueError:
                errors.append(_('No database given for column %s') % column)

        # check permissions on functions
        for function in qp.functions:
            # check permission on function
            function = Function.permissions.get(user, function_name=function_name)
            if not function:
                errors.append(_('Function %s not found.') % function_name)
                continue

        # return the error stack
        return errors
