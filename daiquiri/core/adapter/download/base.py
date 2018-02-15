import logging
import base64
import csv
import io
import six
import struct
import subprocess
import sys
import re

from bitstring import BitArray

logger = logging.getLogger(__name__)


class DownloadAdapter(object):

    def generate(self, format_key, schema_name, table_name, metadata, status=None, empty=False):
        if format_key == 'csv':
            return self.generate_csv(schema_name, table_name)

        elif format_key == 'votable':
            return self.generate_votable('TABLEDATA', schema_name, table_name, metadata, status, empty)

        elif format_key == 'votable-binary':
            return self.generate_votable('BINARY', schema_name, table_name, metadata, status, empty)

        elif format_key == 'votable-binary2':
            return self.generate_votable('BINARY2', schema_name, table_name, metadata, status, empty)

        else:
            raise Exception('Not supported.')

    def generate_csv(self, schema_name, table_name):
        # create the final list of arguments subprocess.Popen
        self.set_table(schema_name, table_name)

        # excecute the subprocess
        process = self.execute()

        if sys.version_info.major >= 3:
            io_class = io.StringIO
        else:
            io_class = io.BytesIO

        for line in process.stdout:
            row = self.parse_line(line)
            if row:
                f = io_class()
                csv.writer(f, quotechar='"').writerow(row)
                yield f.getvalue()

    def generate_votable(self, serialization, schema_name, table_name, metadata, status, empty):
        # create the final list of arguments subprocess.Popen
        self.set_table(schema_name, table_name)

        # excecute the subprocess
        process = self.execute()

        yield '''<?xml version="1.0"?>
<VOTABLE version="1.3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://www.ivoa.net/xml/VOTable/v1.3"
    xmlns:stc="http://www.ivoa.net/xml/STC/v1.30">
    <RESOURCE name="%(database)s" type="results">''' % {
            'database': schema_name
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
                if self.FORMATS[column['datatype']] is not None:
                    attrs = []
                    for key in ['name', 'datatype', 'arraysize', 'unit', 'ucd', 'utype']:
                        if key in column and column[key]:
                            attrs.append('%s="%s"' % (key, column[key]))

                    if serialization == 'BINARY':
                        # for binary specify excplicit null value
                        yield '''
            <FIELD %s>
                <VALUES null="%s" />
            </FIELD>''' % (' '.join(attrs), self.NULL_VALUES[column['datatype']])

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
                parsed_line = self.parse_line(line)
                if parsed_line:
                    if serialization == 'TABLEDATA':
                        yield '''
                    <TR>
                        <TD>%s</TD>
                    </TR>''' % '''</TD>
                        <TD>'''.join([('' if cell == 'NULL' else cell) for cell in parsed_line])

                    elif serialization in ['BINARY', 'BINARY2']:
                        yield self.get_binary_string(metadata['columns'], parsed_line, serialization)

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

    def execute(self):
        # log the arguments
        logger.debug('execute "%s"' % ' '.join(self.args))

        # excecute the subprocess
        try:
            return subprocess.Popen(self.args, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logger.error('Command PIPE returned non-zero exit status: %s' % e)

    def parse_line(self, line):
        insert_pattern = re.compile('^INSERT INTO .*? VALUES \((.*?)\);')
        insert_result = insert_pattern.match(line.decode())
        if insert_result:
            row = insert_result.group(1)
            reader = csv.reader([row], quotechar="'", skipinitialspace=True)
            return six.next(reader)
        else:
            return None

    def get_lists(self, columns):
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

        # log and return
        logger.debug('get_lists fmt_list = %s' % fmt_list)
        logger.debug('get_lists null_value_list = %s' % null_value_list)
        return fmt_list, null_value_list

    def get_binary_string(self, columns, parsed_line, serialization):

        values = []
        null_mask = ''
        fmt_string = '>'
        for i, column in enumerate(columns):
            cell = parsed_line[i]
            fmt = self.FORMATS[column['datatype']]

            if fmt is not None:

                if cell == 'NULL':
                    null_mask += '1'
                    fmt_string += fmt
                    values.append(self.NULL_VALUES[column['datatype']])

                else:
                    null_mask += '0'
                    fmt_string += fmt

                    if fmt in ['B', 'h', 'i', 'q']:
                        values.append(int(cell))

                    elif fmt in ['f', 'd']:
                        values.append(float(cell))

                    else:  # char
                        values.append(cell)

        # log values
        logger.debug('get_binary_string null_mask = %s' % null_mask)
        logger.debug('get_binary_string fmt_string = %s' % fmt_string)
        logger.debug('get_binary_string values = %s' % values)

        # create binary string
        binary_string = struct.pack(fmt_string, *values)

        # prepend the null bitmask for BINARY2
        if serialization == 'BINARY2':
            binary_string = BitArray(bin=null_mask).tobytes() + binary_string

        # convert to base64 and return
        return base64.b64encode(binary_string).decode()
