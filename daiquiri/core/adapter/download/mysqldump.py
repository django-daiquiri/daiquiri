import logging

from .base import BaseDownloadAdapter

logger = logging.getLogger(__name__)


class MysqldumpAdapter(BaseDownloadAdapter):

    def set_args(self, schema_name, table_name, data_only=False):
        self.args = ['mysqldump']
        if data_only:
            self.args += ['--compact', '--skip-extended-insert']

        if self.database_config.get('USER'):
            self.args.append('--user={USER}'.format(**self.database_config))

        if self.database_config.get('PASSWORD'):
            self.args.append('--password={PASSWORD}'.format(**self.database_config))

        if self.database_config.get('HOST'):
            self.args.append('--host={HOST}'.format(**self.database_config))

        if self.database_config.get('PORT'):
            self.args.append('--port={PORT}'.format(**self.database_config))

        self.args.append(schema_name)
        self.args.append(table_name)
