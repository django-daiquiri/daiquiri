import base64
import csv
import io
import re
import six
import struct
import subprocess
import sys

from bitstring import BitArray

from .base import DownloadAdapter


class MysqldumpAdapter(DownloadAdapter):

    insert_pattern = re.compile('^INSERT INTO .*? VALUES \((.*?)\);')

    FORMATS = {
        'char': 'c',
        'unsignedByte': 'B',
        'short': 'h',
        'int': 'i',
        'long': 'q',
        'float': 'f',
        'double': 'd'
    }

    NULL_VALUES = {
        'char': '',
        'unsignedByte': 255,
        'short': 32767,
        'int': 2147483647,
        'long': 9223372036854775807,
        'float': float('nan'),
        'double': float('nan')
    }

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

    def generate(self, format_key, database_name, table_name, metadata, status=None, empty=False):

        if format_key == 'csv':
            return self.generate_csv(database_name, table_name)

        elif format_key == 'votable':
            return self.generate_votable('TABLEDATA', database_name, table_name, metadata, status, empty)

        elif format_key == 'votable-binary':
            return self.generate_votable('BINARY', database_name, table_name, metadata, status, empty)

        elif format_key == 'votable-binary2':
            return self.generate_votable('BINARY2', database_name, table_name, metadata, status, empty)

        else:
            raise Exception('Not supported.')

    def generate_csv(self, database_name, table_name):
        args = self.args + [database_name, table_name]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)

        if sys.version_info.major >= 3:
            io_class = io.StringIO
        else:
            io_class = io.BytesIO

        for line in process.stdout:
            row = self._parse_line(line)
            if row:
                f = io_class()
                csv.writer(f, quotechar='"').writerow(row)
                yield f.getvalue()

    def generate_votable(self, serialization, database_name, table_name, metadata, status, empty):
        args = self.args + [database_name, table_name]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)

        fmt_list, null_value_list = self._get_fmt_list(metadata['columns'])

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
            for i, column in enumerate(metadata['columns']):
                attrs = []
                for key in ['name', 'datatype', 'arraysize', 'unit', 'ucd', 'utype']:
                    if key in column and column[key]:
                        attrs.append('%s="%s"' % (key, column[key]))

                if serialization == 'BINARY':
                    # for binary specify excplicit null value
                    yield '''
            <FIELD %s>
                <VALUES null="%s" />
            </FIELD>''' % (' '.join(attrs), null_value_list[i])

                else:
                    # just yield the field metadata
                    yield '''
            <FIELD %s />''' % ' '.join(attrs)

        if not empty:
            yield '''
            <DATA>'''

            # write serialization specific opening tag
            if serialization == 'TABLEDATA':
                yield '''
                <TABLEDATA>'''
            elif serialization == 'BINARY':
                yield '''
                <BINARY>
                    <STREAM encoding="base64">'''
            elif serialization == 'BINARY2':
                yield '''
                <BINARY2>
                    <STREAM encoding="base64">'''

            # write rows of the table from stdout of the mysqldump process
            for line in process.stdout:
                parsed_line = self._parse_line(line)
                if parsed_line:
                    if serialization == 'TABLEDATA':
                        yield '''
                    <TR>
                        <TD>%s</TD>
                    </TR>''' % '''</TD>
                        <TD>'''.join([('' if cell == 'NULL' else cell) for cell in parsed_line])

                    elif serialization == 'BINARY':
                        values, null_mask = self._get_binary_values(parsed_line, fmt_list, null_value_list)
                        binary_string = struct.pack('>' + ''.join(fmt_list), *values)
                        yield base64.b64encode(binary_string).decode()

                    elif serialization == 'BINARY2':
                        values, null_mask = self._get_binary_values(parsed_line, fmt_list, null_value_list)
                        binary_string = BitArray(bin=null_mask).tobytes() + struct.pack('>' + ''.join(fmt_list), *values)
                        yield base64.b64encode(binary_string).decode()

            # write serialization specific closing tag
            if serialization == 'TABLEDATA':
                yield '''
                </TABLEDATA>'''
            elif serialization == 'BINARY':
                yield '''</STREAM>
                </BINARY>'''
            elif serialization == 'BINARY2':
                yield '''</STREAM>
                </BINARY2>'''

            yield '''
            </DATA>'''
        yield '''
        </TABLE>
    </RESOURCE>
</VOTABLE>
'''

    def _get_fmt_list(self, columns):
        fmt_list = []
        null_value_list = []
        for column in columns:
            if column['arraysize'] is not None:
                if column['datatype'] == 'char':
                    # this is a string!
                    fmt_list.append(str(column['arraysize']) + 's')
                else:
                    fmt_list.append(str(column['arraysize']) + self.FORMATS[column['datatype']])

                null_value_list.append('')
            else:
                fmt_list.append(self.FORMATS[column['datatype']])
                null_value_list.append(self.NULL_VALUES[column['datatype']])

        return fmt_list, null_value_list

    def _parse_line(self, line):
        insert_result = self.insert_pattern.match(line.decode())
        if insert_result:
            row = insert_result.group(1)
            reader = csv.reader([row], quotechar="'")
            return six.next(reader)
        else:
            return None

    def _get_binary_values(self, parsed_line, fmt_list, null_value_list):
        values = []
        null_mask = ''

        for i, cell in enumerate(parsed_line):
            if cell == 'NULL':
                null_mask += '1'
                values.append(null_value_list[i])

            else:
                null_mask += '0'

                if fmt_list[i] in ['B', 'h', 'i', 'q']:
                    values.append(int(cell))

                elif fmt_list[i] in ['f', 'd']:
                    values.append(float(cell))

                else:  # char
                    values.append(cell)

        return values, null_mask
