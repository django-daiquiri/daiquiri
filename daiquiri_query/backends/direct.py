from django.utils.timezone import now

from daiquiri_core.adapter import get_adapter
from daiquiri_uws.settings import PHASE_COMPLETED

from .base import BaseQueryBackend


class DirectQueryBackend(BaseQueryBackend):

    def submit(self, job):
        adapter = get_adapter('data')

        # set database and start time
        job.database_name = self.get_user_database_name(job.owner.username)
        job.start_time = now()

        # get the actual query and submit the job to the database
        job.actual_query = adapter.submit_direct_query(job.database_name, job.table_name, job.query)

        # gt additional information about the finished job and save the job object
        job.end_time = now()
        job.execution_duration = (job.end_time - job.start_time).seconds
        job.nrows, job.size = adapter.fetch_stats(job.database_name, job.table_name)
        job.metadata = adapter.fetch_table(job.database_name, job.table_name)
        job.metadata['columns'] = adapter.fetch_columns(job.database_name, job.table_name)
        job.phase = PHASE_COMPLETED
        job.save()

    def get_user_database_name(self, username):
        return 'daiquiri_user_' + username
