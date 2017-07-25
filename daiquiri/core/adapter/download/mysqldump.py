import csv
import io
import re
import subprocess

from .base import DownloadAdapter


class MysqldumpAdapter(DownloadAdapter):

    insert_pattern = re.compile('^INSERT INTO .*? VALUES \((.*?)\);')

    def __init__(self, database_key, database_config):
        self.args = ['mysqldump', '--compact', '--skip-extended-insert']

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

    def generate(self, format_key, database_name, table_name, metadata, status=None):

        if format_key == 'csv':
            return self.generate_csv(database_name, table_name, metadata, status)

        elif format_key == 'votable':
            return self.generate_votable(database_name, table_name, metadata, status)

        else:
            raise Exception('Not supported.')

    def generate_csv(self, database_name, table_name, metadata, status):
        args = self.args + [database_name, table_name]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)

        for line in process.stdout:
            row = self.parse_line(line)
            if row:
                f = io.BytesIO()
                csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL).writerow(row)
                yield f.getvalue()

    def generate_votable(self, database_name, table_name, metadata, status):
        args = self.args + [database_name, table_name]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)

        yield '''<?xml version="1.0"?>
<VOTABLE version="1.3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://www.ivoa.net/xml/VOTable/v1.3"
    xmlns:stc="http://www.ivoa.net/xml/STC/v1.30">
    <RESOURCE name="%(database)s" type="results">''' % {
            'database': database_name
        }
        if status == 'OK':
            yield '''
        <INFO name="QUERY_STATUS" value="OK" />'''
        elif status == 'OVERFLOW':
            yield '''
        <INFO name="QUERY_STATUS" value="OVERFLOW" />'''

        yield '''
        <TABLE name="%(table)s">''' % {
            'table': table_name
        }

        if 'columns' in metadata:
            for column in metadata['columns']:
                attrs = []
                for key in ['name', 'datatype', 'arraysize', 'unit', 'ucd', 'utype']:
                    if key in column and column[key]:
                        attrs.append('%s="%s"' % (key, column[key]))

                yield '''
            <FIELD %s />''' % ' '.join(attrs)

        first = True
        for line in process.stdout:
            parsed_line = self.parse_line(line)
            if parsed_line:
                if first:
                    first = False
                    yield '''
            <DATA>'''

                    yield '''
                <TABLEDATA>'''

                yield '''
                <TR>
                    <TD>%s</TD>
                </TR>''' % '''</TD>
                    <TD>'''.join(parsed_line)

        if first is False:
            yield '''
                </TABLEDATA>'''

            yield '''
            </DATA>'''
        yield '''
        </TABLE>
    </RESOURCE>
</VOTABLE>
'''
