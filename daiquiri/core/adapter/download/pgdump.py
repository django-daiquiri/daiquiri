import logging

from .base import BaseDownloadAdapter

logger = logging.getLogger(__name__)


class PgDumpAdapter(BaseDownloadAdapter):

    def set_args(self, schema_name, table_name, data_only=False):
        # command line for pg_dump:
        # pg_dump ... --dbname=postgresql://user:password@host:port/database --table=schema.table
        # pg_dump ... --user=user --host=host --port=port --dbname=database --table=schema.table

        self.args = ['pg_dump', '--no-owner']
        if data_only:
            self.args += ['--data-only', '--inserts']

        if self.database_config.get('PASSWORD'):
            if self.database_config.get('PORT'):
                dbname = '--dbname=postgresql://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(NAME)s'
            else:
                dbname = '--dbname=postgresql://%(USER)s:%(PASSWORD)s@%(HOST)s/%(NAME)s'

            self.args.append(dbname % self.database_config)
        else:
            if self.database_config.get('USER'):
                self.args.append('--user={USER}'.format(**self.database_config))

            if self.database_config.get('HOST'):
                self.args.append('--host={HOST}'.format(**self.database_config))

            if self.database_config.get('PORT'):
                self.args.append('--port=%(PORT)d' % self.database_config)

            self.args.append('--dbname={NAME}'.format(**self.database_config))

        self.args.append(f'--table="{schema_name}"."{table_name}"')
