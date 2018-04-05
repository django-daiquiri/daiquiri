import logging

from .base import BaseDownloadAdapter

logger = logging.getLogger(__name__)


class MysqldumpAdapter(BaseDownloadAdapter):

    def set_args(self, schema_name, table_name):
        self.args = ['mysqldump', '--compact', '--skip-extended-insert']

        if 'USER' in self.database_config and self.database_config['USER']:
            self.args.append('--user=%(USER)s' % self.database_config)

        if 'PASSWORD' in self.database_config and self.database_config['PASSWORD']:
            self.args.append('--password=%(PASSWORD)s' % self.database_config)

        if 'HOST' in self.database_config and self.database_config['HOST']:
            self.args.append('--host=%(HOST)s' % self.database_config)

        if 'PORT' in self.database_config and self.database_config['PORT']:
            self.args.append('--port=%(PORT)s' % self.database_config)

        self.args.append(schema_name)
        self.args.append(table_name)
