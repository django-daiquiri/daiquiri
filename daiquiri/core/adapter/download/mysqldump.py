import csv
import io
import json
import os
import pipes
import re
import subprocess

from .base import DownloadAdapter


class MysqldumpAdapter(DownloadAdapter):

    insert_pattern = re.compile('^INSERT INTO .*? VALUES \((.*?)\);')

    def __init__(self, database_key, database_config):
        self.args = ['mysqldump','--compact','--skip-extended-insert']

        if 'USER' in database_config and database_config['USER']:
            self.args.append('--user=%(USER)s' % database_config)

        if 'PASSWORD' in database_config and database_config['PASSWORD']:
            self.args.append('--password=%(PASSWORD)s' % database_config)

        if 'HOST' in database_config and database_config['HOST']:
            self.args.append('--host=%(HOST)s' % database_config)

        if 'PORT' in database_config and database_config['PORT']:
            self.args.append('--port=%(PORT)s' % database_config)

    def parse_line(self, line):
        insert_result = self.insert_pattern.match(line)
        if insert_result:
            row = insert_result.group(1)
            reader = csv.reader([row], quotechar="'")
            return reader.next()
        else:
            return None

    def generate(self, format_key, database_name, table_name, metadata):

        if format_key == 'csv':
            return self.generate_csv(database_name, table_name, metadata)

        elif format_key == 'votable':
            return self.generate_votable(database_name, table_name, metadata)

        else:
            raise Exception('Not supported.')

    def generate_csv(self, database_name, table_name, metadata):
        args = self.args + [database_name, table_name]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)

        for line in process.stdout:
            row = self.parse_line(line)
            if row:
                f = io.BytesIO()
                csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL).writerow(row)
                yield f.getvalue()

    def generate_votable(self, database_name, table_name, metadata):
        args = self.args + [database_name, table_name]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)

        yield '''<?xml version="1.0"?>
<VOTABLE version="1.3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://www.ivoa.net/xml/VOTable/v1.3"
    xmlns:stc="http://www.ivoa.net/xml/STC/v1.30">
    <RESOURCE name="%(database)s" type="results">
        <INFO name="QUERY_STATUS" value="OK" />
        <TABLE name="%(table)s">''' % {
            'database': database_name,
            'table': table_name
        }

        if 'columns' in metadata:
            for column in metadata['columns']:
                yield '''
            <FIELD name="%(name)s" datatype="%(datatype)s"/>''' % column

        yield '''
            <DATA>'''

        yield '''
                <TABLEDATA>'''


        for line in process.stdout:
            parsed_line = self.parse_line(line)
            if parsed_line:
                yield '''
                <TR>
                    <TD>%s</TD>
                </TR>''' % '''</TD>
                    <TD>'''.join(parsed_line)

        yield '''
                </TABLEDATA>'''

        yield '''
            </DATA>
        </TABLE>
    </RESOURCE>
</VOTABLE>
'''
