import csv
import io
import logging
import struct
from datetime import datetime, timezone
from xml.sax.saxutils import escape, quoteattr

from django.contrib.sites.models import Site

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import create_engine

from daiquiri import __version__ as daiquiri_version

logger = logging.getLogger(__name__)


def generate_csv(generator, fields):
    # write header
    f = io.StringIO()
    csv.writer(f, quotechar='"').writerow([field['name'] for field in fields])
    yield f.getvalue()

    for row in generator:
        if row:
            # convert curl brace to square brace in all array-like columns
            corrected_row = []
            for col in row:
                corrected_col = col

                if isinstance(col, str):
                    if col.startswith('{') and col.endswith('}'):
                        corrected_col = col.replace('{', '[').replace('}', ']')

                corrected_row = [*corrected_row, corrected_col]

            f = io.StringIO()
            csv.writer(f, quotechar='"').writerow(corrected_row)

            yield f.getvalue()


def correct_col_for_votable(col):
    corrected_col = col

    if col.startswith('{') and col.endswith('}'):  # this is an array
        # remove {} and replace , with space
        corrected_col = col.replace('{', '').replace('}', '').replace(',', ' ')

    return corrected_col


def generate_votable(generator, fields, infos=[], links=[], services=[], table=None, empty=False):
    yield """<?xml version="1.0"?>
<VOTABLE version="1.3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://www.ivoa.net/xml/VOTable/v1.3"
    xmlns:stc="http://www.ivoa.net/xml/STC/v1.30">"""

    yield """
    <RESOURCE type="results">"""

    for key, value in infos:
        if value is not None:
            yield f"""
            <INFO name={quoteattr(key)} value={quoteattr(value)} />"""

    for title, content_role, href in links:
        yield f"""
        <LINK title={quoteattr(title)} content-role={quoteattr(content_role)} href={quoteattr(href)}/>"""  # noqa: E501

    if table is not None:
        yield f'''
        <TABLE name="{table}">'''
    else:
        yield """
        <TABLE>"""

    for field in fields:
        attrs = []
        for key in ['name', 'unit', 'ucd', 'utype']:
            if field.get(key):
                value = (
                    field[key]
                    .replace('&', '&amp;')
                    .replace('"', '&quot;')
                    .replace("'", '&apos;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                )
                attrs.append(f'{key}="{value}"')

        if field.get('ucd'):
            if 'meta.id' in field['ucd'] and 'meta.ref' in field['ucd']:
                attrs.append('ID="datalinkID"')

        if 'arraysize' in field:
            if field.get('datatype') == 'char' and field['arraysize'] is None:
                attrs.append('arraysize="*"')
            elif field['arraysize']:
                attrs.append('arraysize="{}"'.format(field['arraysize']))

        if 'datatype' in field:
            if field['datatype'] in [
                'boolean',
                'char',
                'unsignedByte',
                'short',
                'int',
                'long',
                'float',
                'double',
            ]:
                attrs.append('datatype="{}"'.format(field['datatype']))

            elif field['datatype'] in [
                'short[]',
                'int[]',
                'long[]',
                'float[]',
                'double[]',
            ]:
                attrs.append(f'datatype="{field["datatype"].rstrip("[]")}"')
                if field['arraysize']:
                    attrs.append(f'arraysize="{field["arraysize"]}"')
                else:
                    attrs.append('arraysize="*"')

            else:
                attrs.append('xtype="{}"'.format(field['datatype']))

        if attrs:
            yield """
            <FIELD {} />""".format(' '.join(attrs))

    # fmt: off
    if not empty:
        yield """
            <DATA>
                <TABLEDATA>"""

        # write rows of the table yielded by the generator
        for row in generator:
            yield """
                    <TR>
                        <TD>{}</TD>
                    </TR>""".format(
                """</TD>
                        <TD>""".join(
                    [('' if cell in ['NULL', None] else correct_col_for_votable(escape(str(cell)))) for cell in row] # noqa : E501
                )
            )

        yield """
                </TABLEDATA>
            </DATA>"""
    yield """
        </TABLE>
    </RESOURCE>"""

    for service in services:
        yield """
    <RESOURCE type="meta" utype="adhoc:service">"""
        for param in service.get('params', []):
            yield """
        <PARAM name="{name}" datatype="{datatype}" arraysize="{arraysize}" value="{value}" />""".format(**param) # noqa : E501
        for group in service.get('groups', []):
            yield """
        <GROUP name="{name}">""".format(**group)
            for param in group.get('params', []):
                yield """
            <PARAM name="{name}" datatype="{datatype}" arraysize="{arraysize}" value="{value}" ref="{ref}"/>""".format(**param) # noqa : E501
            yield """
        </GROUP>"""
        yield """
    </RESOURCE>"""
    yield """
</VOTABLE>
"""


# fmt: on


def generate_fits(generator, fields, nrows, table_name=None, array_infos={}):
    DEFAULT_CHAR_SIZE = 256

    # VO format label, FITS format label, size in bytes, NULL value, encoded value
    # fmt:off
    formats_dict = {
        'boolean':   ('s', 'L', 1,  b'\x00',             lambda x: b'T' if x == 'true' else b'F'), #noqa: E501
        'short':     ('h', 'I', 2,  32767,               int),
        'int':       ('i', 'J', 4,  2147483647,          int),
        'long':      ('q', 'K', 8,  9223372036854775807, int),
        'float':     ('f', 'E', 4,  float('nan'),        float),
        'double':    ('d', 'D', 8,  float('nan'),        float),
        'char':      ('s', 'A', 32, b'',                 lambda x: x.encode()),
        'timestamp': ('s', 'A', 19, b'',                 lambda x: x.encode()),
        'array':     ('s', 'A', 64, b'',                 lambda x: x.encode()),
        'spoint':    ('s', 'A', 64, b'',                 lambda x: x.encode()),
        'unknown':   ('s', 'A', 8,  b'',                 lambda x: x.encode()),
        'short[]':   ('h', 'I', 2,  32767,               int),
        'int[]':     ('i', 'J', 4,  2147483647,          int),
        'long[]':    ('q', 'K', 8,  9223372036854775807, int),
        'float[]':   ('f', 'E', 4,  float('nan'),        float),
        'double[]':  ('d', 'D', 8,  float('nan'),        float),
        'char[]':    ('s', 'A', 32, b'',                 lambda x: x.encode()),
    }
    # fmt:on

    names = [field['name'] for field in fields]
    datatypes = [field['datatype'] for field in fields]
    arraysizes = [field.get('arraysize') or '' for field in fields]
    descriptions = [field.get('description') or '' for field in fields]

    for i, (datatype, arraysize) in enumerate(zip(datatypes, arraysizes)):
        if datatype == 'timestamp':
            arraysizes[i] = formats_dict['timestamp'][2]
        elif datatype in ('char', 'spoint', 'array') and arraysize == '':
            arraysizes[i] = formats_dict[datatype][2]
        elif datatype is None:
            datatypes[i] = 'unknown'
            arraysizes[i] = formats_dict['unknown'][2]

    units = []
    ucds = []
    for field in fields:
        if 'unit' in field and field['unit'] is not None:
            units.append(field['unit'])
        else:
            units.append('')
        if 'ucd' in field and field['ucd'] is not None:
            ucds.append(field['ucd'])
        else:
            ucds.append('')

    naxis1_list = []

    for datatype, arraysize, name in zip(datatypes, arraysizes, names):
        if '[]' in datatype:
            if datatype == 'char[]':
                naxis1_list.append(array_infos[name] * DEFAULT_CHAR_SIZE)
            else:
                naxis1_list.append(array_infos[name] * formats_dict[datatype][2])
        else:
            naxis1_list.append(formats_dict[datatype][2] if not arraysize else arraysize)

    naxis1 = sum(naxis1_list)
    naxis2 = nrows
    tfields = len(names)

    logo = get_daiquiri_logo(str(Site.objects.get_current())[:30], daiquiri_version)

    # Main header #############################################################
    # fmt:off
    header0info = [
        ('SIMPLE',  'T',       'conforms to FITS standard'),
        ('BITPIX',  '8',       'array data type'),
        ('NAXIS',   '1',       'number of array dimensions'),
        ('NAXIS1',  '2880',    'number of characters'),
        ('EXTEND',  'T',       ''),
        ('NTABLE',  '1',       ''),
        ('LONGSTRN','OGIP 1.0','The OGIP long string convention may be used.'),
        ('COMMENT', 'This FITS file may contain long string keyword values that are',''),
        ('COMMENT', 'continued over multiple keywords.  This convention uses the  "&"',''),
        ('COMMENT', 'character at the end of a string which is then continued', ''),
        ('COMMENT', 'on subsequent keywords whose name = "CONTINUE".', ''),
        ('END',     '',        ''),
    ]
    # fmt:on

    h0 = ''.join([create_fits_card(*entry) for entry in header0info])
    h0 += ' ' * (2880 * (len(h0) // 2880 + 1) - len(h0))

    yield h0.encode()

    # Main table content - required by some FITS viewers ######################
    yield (logo + '\x00' * (2880 - len(logo))).encode()

    # Table header ############################################################
    # fmt:off
    header1info = [
        ('XTENSION', "'BINTABLE'", 'binary table extension    '),
        ('BITPIX',   '8',          'array data type    '),
        ('NAXIS',    '2',          'number of array dimensions    '),
        ('NAXIS1',  f'{naxis1}',   'length of dimension 1    '),
        ('NAXIS2',  f'{naxis2}',   'length of dimension 2    '),
        ('PCOUNT',   '0',          'number of group parameters    '),
        ('GCOUNT',   '1',          'number of groups    '),
        ('TFIELDS', f'{tfields} ', 'number of table fields    '),
    ]
    # fmt:on

    if table_name is not None:
        # table_name needs to be shorter than 50 chars
        header1info.append(('EXTNAME', f"'{table_name[:50]}'", 'table name '))

    h1 = ''.join([create_fits_card(*entry) for entry in header1info])

    for i, (name, datatype, arraysize, unit, ucd, description) in enumerate(
        zip(names, datatypes, arraysizes, units, ucds, descriptions)
    ):
        if '[]' not in datatype:
            format_str = (str(arraysize) + formats_dict[datatype][1]).ljust(8)
        else:
            if datatype == 'char[]':
                format_str = str(array_infos[name] * DEFAULT_CHAR_SIZE) + formats_dict[datatype][1]
            else:
                format_str = str(array_infos[name]) + formats_dict[datatype][1].ljust(8)

        h1 += create_fits_card(f'TTYPE{i + 1}', f"'{name.ljust(8)}'", f'label for col {i + 1}    ')
        h1 += create_fits_card(f'TFORM{i + 1}', f"'{format_str}'", f'format for col {i + 1}    ')

        # NULL values only for int-like types
        if datatype in (
            'short',
            'int',
            'long',
        ):
            h1 += create_fits_card(
                f'TNULL{i + 1}',
                formats_dict[datatype][3],
                f'blank value for col {i + 1}    ',
            )

        if unit:
            h1 += create_fits_card(
                f'TUNIT{i + 1}', f"'{unit.ljust(8)}'", f'unit for col {i + 1}    '
            )

        if ucd:
            h1 += create_fits_card(f'TUCD{i + 1}', f"'{ucd.ljust(8)}'", f'ucd for col {i + 1}    ')

        if description:
            for line in create_fits_card(
                f'TCOMM{i + 1}', f'{description}', f'desc for col {i + 1}    '
            ):
                h1 += line

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    h1 += create_fits_card('DATE-HDU', f"'{now}'", 'UTC date of HDU creation')
    h1 += create_fits_card('END', '', '')
    h1 += ' ' * (2880 * (len(h1) // 2880 + 1) - len(h1))

    yield h1.encode()

    # Data ####################################################################
    fmt = '>' + ''.join(
        [
            str(arraysize) + formats_dict[datatype][0]
            for datatype, arraysize in zip(datatypes, arraysizes)
        ]
    )

    row_count = 0

    for row in generator:
        fmt = '>'
        row_elements_formatted = []
        for row_element, datatype, arraysize, name in zip(row, datatypes, arraysizes, names):
            if row_element == 'NULL':
                r = formats_dict[datatype][3]
                f = str(arraysize) + formats_dict[datatype][0]
                row_elements_formatted.append(r)
            elif datatype[-2:] == '[]':
                r = []
                parsed = parse_and_fill_fits_array(
                    obj_str=row_element,
                    obj_type=datatype,
                    desired_length=array_infos[name],
                    formats_dict=formats_dict,
                )
                for j in parsed:
                    if j == 'NULL':
                        entry = formats_dict[datatype][3]
                    else:
                        entry = formats_dict[datatype][4](j)
                    r.append(entry)
                f = str(array_infos[name]) + formats_dict[datatype][0]
                if datatype == 'char[]':
                    f = str(array_infos[name] * DEFAULT_CHAR_SIZE) + formats_dict[datatype][0]

                if datatype != 'char[]':
                    row_elements_formatted.extend(r)
                else:
                    row_elements_formatted.append(b''.join(r))

            else:
                r = formats_dict[datatype][4](row_element)
                f = str(arraysize) + formats_dict[datatype][0]
                row_elements_formatted.append(r)
            fmt += f
        yield struct.pack(fmt, *row_elements_formatted)

        row_count += 1

    # Footer padding (to fill the last block to 2880 bytes) ###################
    ln = naxis1 * row_count
    footer = '\x00' * (2880 * (ln // 2880 + 1) - ln)

    yield footer.encode()


def create_fits_card(key: str, val: str, comment: str) -> str:
    key_length = 8
    line_length = 80
    value_length = line_length - key_length - len(comment)
    line = key[:key_length].ljust(key_length)

    total_size = 15 + len(comment) + len(str(val))

    lines = []

    if not total_size > line_length:
        if val != '':
            if 'TCOMM' in key:
                if val[0] != "'":
                    val = f"'{val}'"
            line += '=' + f' {val} '[: value_length - 1].rjust(key_length, ' ')

            line = line[:line_length]
        if comment != '':
            line += f' / {comment}'
        line = line.ljust(line_length)
        return line
    else:
        reststr = val
        i = 0
        while len(reststr) > 0:
            if i == 0:
                line = key[:key_length].ljust(key_length) + '= '
            else:
                line = 'CONTINUE  '
            line += f"'{reststr[:60]}&'"
            reststr = reststr[60:]
            if len(reststr) == 0:
                if len(comment) < line_length - len(line) - 3:
                    line = line[:-2] + "'" + f' / {comment}'
                    line = line.ljust(line_length)
                    lines.append(line)
                else:
                    line = line.ljust(line_length)
                    lines.append(line)
                    line = "CONTINUE  '  '"
                    line += f' / {comment}'
                    line = line.ljust(line_length)
                    lines.append(line)
            else:
                line = line.ljust(line_length)
                lines.append(line)
            i += 1

        return ''.join(lines)


def get_daiquiri_logo(site: str, version: str) -> str:
    site_str = (' ' * (15 - len(site) // 2) + site).ljust(30)
    logo = f"""
                                  `,......`
                               :::.````````...
                             ::``,:::,`.....``..`
                           ,:.`,``,:::`....`````..
                          .:``:::,``,:`::```...``..
                          :,`::::::,`````,::::::`.:
                          :::::::::::::::::::::::::
         '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
         ,:,,,,,,,,,,,,,,,,,,,,,,,,,,,,,............................
           :,,,`````````...,,,,,,,,............................```
             ,,,.```````...,,,,,,,,............................`
              `,,,``````....,,,,,,,...........................`
                :+++,,,,,::::+++++++++++++++++++++++++++++++'
                  \\\\     created with django-daiquiri     //
                    \\\\               v{version.ljust(18)}//
                      \\\\{site_str}//
                        ,,,.....,,,..................`
                         :++':;;;++++++++++++++++++'
                           ,,,,,,,::::;;;;;;;;''''
                             ,,,................
                               ,,,............
                                 ,,.........`
                                  `;;;;;;;:
                                   ,'` `''
                                    :: ::
                                     . .`
        +++++++++:             ,                       ,          .,
         +++    +++           '+'                     '+'         ++.
         +++    ,++:  :'+'.  `'+'   ,'';'+ ;'+` .'+' `'+' .++,:+ ;++`
         +++    `++; ++  '';  ;'; `''  `''  ''`  ;''  ;''  ;++:,  ++`
         +++    ;++. :++''''  ;'; ;''  `''  ''`  ;''  ;''  ;+'    ++`
         +++  `+++: .++  '''  ;'' .''  .''  '',  '''  ;''  '+'    ++`
        +++++++:     `'+'`+',,+++,  ;+'.++   ;++: +'.,+++,,++++. ++++
                                      `+++.

    """
    return logo


def parse_and_fill_fits_array(
    obj_str: str, obj_type: str, desired_length: int, formats_dict: dict
) -> list:
    array = list(obj_str.strip('{}').split(','))

    if obj_type == 'char[]':
        array = [f'{i}_' for i in array[:-1]] + [f'{array[-1]}']

    for _ in range(desired_length - len(array)):
        if obj_type in ['float[]', 'double[]']:
            array.append(formats_dict[obj_type][3])
        elif obj_type == 'char[]':
            array.append('')
        elif obj_type in ['short[]', 'int[]', 'long[]']:
            array.append(formats_dict[obj_type][3])
        else:
            raise ValueError(f'Unknown array type: {obj_type}')

    return array


def generate_parquet(
    schema_name: str, table_name: str, fields: dict, metadata: str, database_config: dict
):
    PQ_TYPE_MAP = {
        'boolean': pa.bool_(),
        'short': pa.int16(),
        'int': pa.int32(),
        'long': pa.int64(),
        'float': pa.float32(),
        'double': pa.float64(),
        'short[]': pa.list_(pa.int16()),
        'int[]': pa.list_(pa.int32()),
        'long[]': pa.list_(pa.int64()),
        'float[]': pa.list_(pa.float32()),
        'double[]': pa.list_(pa.float64()),
        'char': pa.string(),
        'string': pa.string(),
        'unicodeChar': pa.string(),
        'timestamp': pa.timestamp('us'),
    }
    if database_config['PORT'] == '':
        database_config['PORT'] = 5432

    query = f'SELECT * FROM "{schema_name}"."{table_name}"'

    db_url = (
        f'postgresql+psycopg://{database_config["USER"]}:'
        f'{database_config["PASSWORD"]}@{database_config["HOST"]}:'
        f'{database_config["PORT"]}/{database_config["NAME"]}'
    )

    engine = create_engine(db_url)
    connection = engine.connect().execution_options(stream_results=True)

    arrow_fields = []
    for f in fields:
        dt = f['datatype']
        if dt not in PQ_TYPE_MAP:
            dt = pa.string()
        arrow_fields.append(pa.field(f['name'], PQ_TYPE_MAP[dt]))
    schema = pa.schema(arrow_fields)

    sink = YieldingWriter()
    buffer = pa.PythonFile(sink)
    writer = pq.ParquetWriter(buffer, schema, compression='zstd')

    kv_meta = {
        b'IVOA.VOTable-Parquet.version': b'1.0',
        b'IVOA.VOTable-Parquet.content': metadata.encode('utf-8'),
    }
    writer.add_key_value_metadata(kv_meta)

    try:
        for chunk in pd.read_sql(query, con=connection, chunksize=100000):
            table = pa.Table.from_pandas(chunk, preserve_index=False).cast(schema)
            writer.write_table(table)

            data = sink.get_and_reset()
            if data:
                yield data

        writer.close()

        data = sink.get_and_reset()
        if data:
            yield data

    finally:
        connection.close()


class YieldingWriter(io.RawIOBase):
    """A write-only file-like object that yields bytes progressively."""

    def __init__(self):
        self.buffer = bytearray()
        self.closed_flag = False

    def writable(self):
        return True

    def write(self, b):
        self.buffer.extend(b)
        return len(b)

    def close(self):
        self.closed_flag = True
        return super().close()

    def get_and_reset(self):
        """Return accumulated bytes and reset buffer."""
        if not self.buffer:
            return b''
        data = bytes(self.buffer)
        self.buffer.clear()
        return data
