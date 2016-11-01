from django.utils.timezone import now

from daiquiri_core.adapter import get_adapter
from daiquiri_uws.settings import PHASE_COMPLETED

from .base import BaseQueryBackend


class DirectQueryBackend(BaseQueryBackend):

    def submit(self, job):
        adapter = get_adapter('data')
        database_name = self.get_user_db(job.owner.username)
        table_name = job.tablename

        job.start_time = now()
        job.actual_query = adapter.submit_direct_query(database_name, table_name, job.query)
        job.end_time = now()
        job.execution_duration = (job.end_time - job.start_time).seconds
        job.nrows, job.size = adapter.fetch_stats(database_name, table_name)
        job.phase = PHASE_COMPLETED

        job.save()

    def get_user_db(self, username):
        return 'daiquiri_user_' + username
