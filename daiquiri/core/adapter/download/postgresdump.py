import logging
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

logger = logging.getLogger(__name__)

class PostgreSQLdumpAdapter(DownloadAdapter):

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
        # TODO: argument string to pass
        # command line for pg_dump:
        # pg_dump --dbname=postgresql://user:password@host:port/database --table=schema.table 

        self.args = ['pg_dump']

        dbname_arg = '--dbname=postgresql://'

        if 'USER' in database_config and database_config['USER']:
            dbname_arg += '%(USER)s' % database_config

        dbname_arg +=':' 

        if 'PASSWORD' in database_config and database_config['PASSWORD']:
            dbname_arg +='%(PASSWORD)s' % database_config
        
        dbname_arg +='@' 

        if 'HOST' in database_config and database_config['HOST']:
            dbname_arg +='%(HOST)s' % database_config

        if 'PORT' in database_config and database_config['PORT']:
            dbname_arg +=':%(PORT)s' % database_config
        
        dbname_arg +='/' 

        if 'NAME' in database_config and database_config['NAME']:
            dbname_arg +='%(NAME)s' % database_config

        self.args.append(dbname_arg)

        
    def _set_args(self, schema_name, table_name):
        # append --table=schema.table
        self.args.append('--table=%s.%s' % (schema_name, table_name))
        return self.args

    def generate(self, format_key, schema_name, table_name, metadata, status=None, empty=False):

        logger.debug('postgres generate %s' % format_key)

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
        args = self._set_args(self, schema_name, table_name)
        try: 
            process = subprocess.Popen(args, stdout=subprocess.PIPE)
        except CalledProcessError as e:
            logger.error('Command PIPE returned non-zero exit status: %s' % e)

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

    def generate_votable(self, serialization, schema_name, table_name, metadata, status, empty):
        args = self._set_args(self, schema_name, table_name)

        process = subprocess.Popen(args, stdout=subprocess.PIPE)

        fmt_list, null_value_list = self._get_fmt_list(metadata['columns'])

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
