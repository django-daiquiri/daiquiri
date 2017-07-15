import csv
import json
import os
import pipes
import re
import subprocess

from .base import DownloadAdapter


class MysqldumpAdapter(DownloadAdapter):

    def __init__(self, database_key, database_config):
        pass

    def write_table(self, stream, database_name, table_name, format):
        pass

    # def _get_stream_table_cmd(self, database_name, table_name):
    #     cmd = 'mysqldump --user=\'%(USER)s\' --password=\'%(PASSWORD)s\'' % self.database_config

    #     if self.database_config['HOST']:
    #         cmd += ' --host=\'%(HOST)s\'' % self.database_config

    #     if self.database_config['PORT']:
    #         cmd += ' --port=\'%(PORT)s\'' % self.database_config

    #     cmd += ' --skip-extended-insert %(database)s %(table)s' % {
    #         'database': pipes.quote(database_name),
    #         'table': pipes.quote(table_name)
    #     }

    #     return cmd

    # def dump_table_csv(self, database_name, table_name, file_name):
    #     # get column names
    #     column_names = self.fetch_column_names(database_name, table_name)

    #     with open(file_name, 'wb') as csvfile:
    #         writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #         writer.writerow(column_names)

    #     # construct sed regexp
    #     sed_cmd = (
    #         # remove the INSERT INTO command
    #         's/^.*VALUES (//g',
    #         # replace end of row with a new line
    #         's/),(/\\n/g',
    #         # remove ); at the end
    #         's/);$//g',
    #         # convert ' to ""
    #         's/\\x27/"/g'
    #     )

    #     cmd = self._get_stream_table_cmd(database_name, table_name)
    #     cmd += ' | sed \'%s\'' % ';'.join(sed_cmd)
    #     cmd += ' >> ' + file_name

    #     subprocess.check_call(cmd, shell=True)

    # def stream_table_csv(self, database_name, table_name):

    #     cmd = self._get_stream_table_cmd(database_name, table_name)

    #     process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, bufsize=-1)
    #     return process.communicate()[0]

    # def dump_table_votable(self, database_name, table_name, file_name):
    #     # get column names and metadata
    #     column_names = self.fetch_column_names(database_name, table_name)
    #     columns = self.fetch_columns(database_name, table_name)

    #     # write header
    #     header = '<?xml version="1.0"?><VOTABLE version="1.3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.ivoa.net/xml/VOTable/v1.3" xmlns:stc="http://www.ivoa.net/xml/STC/v1.30" ><RESOURCE name="%(database)s"><TABLE name="%(table)s">' % {
    #         'database': database_name,
    #         'table': table_name
    #     }

    #     for column_name, column in zip(column_names, columns):
    #         column['name'] = column_name
    #         header += '<FIELD name="%(name)s" datatype="%(datatype)s"/>' % column

    #     header += '<DATA><TABLEDATA>'

    #     with open(file_name, 'wb') as f:
    #         f.write(header)

    #     # construct sed regexp
    #     sed_cmd = (
    #         # replace the INSERT INTO command with <TR><TD>
    #         's/^.*VALUES (/<TR><TD>/g',
    #         # replace end of row with </TD></TR>
    #         's/),(/<\/TD><\/TR><TR><TD>/g',
    #         # replace , with </TD><TD>
    #         's/,/<\/TD><TD>/g',
    #         # replace ); at the end with </TD></TR>
    #         's/);$/<\/TD><\/TR>/g',
    #     )

    #     # write table data
    #     cmd = self._get_stream_table_cmd(database_name, table_name)
    #     cmd += ' | sed \'%s\'' % ';'.join(sed_cmd)
    #     cmd += ' >> ' + file_name

    #     subprocess.check_call(cmd, shell=True)

    #     # write footer
    #     footer = '</TABLEDATA></DATA></TABLE></RESOURCE></VOTABLE>'
    #     cmd = 'echo \'%s\' >> %s' % (footer, file_name)
    #     subprocess.check_call(cmd, shell=True)
