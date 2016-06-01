from datetime import datetime

from django.db import models
from django.conf import settings

from daiquiri_jobs.models import Job
from daiquiri_uws.settings import PHASE_PENDING


class QueryJobsSubmissionManager(models.Manager):

    def submit(self, query, user, tablename=None, queue=None):

        tablename = self._get_tablename(tablename)
        queue = self._get_queue(queue)

        # check sanity (table exists etc.)

        # translate query -> mysql string

        # parse mysql string -> parser object

        # check syntax

        # permission on databases/tables/functions/keywords/(columns)

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
