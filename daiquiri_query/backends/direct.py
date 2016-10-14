from daiquiri_core.adapter import get_adapter

from .base import BaseQueryBackend


class DirectQueryBackend(BaseQueryBackend):

    def submit(self, job):
        adapter = get_adapter('data')
        database_name = self.get_user_db(job.owner.username)
        table_name = job.tablename
        actual_query = adapter.submit_direct_query(database_name, table_name, job.query)
        print (actual_query)

    def get_user_db(self, username):
        return 'daiquiri_user_' + username
