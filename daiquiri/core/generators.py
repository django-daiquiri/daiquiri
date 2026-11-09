import csv
import io
import logging
import struct
import tempfile
from datetime import datetime, timezone
from xml.sax.saxutils import escape, quoteattr

from django.conf import settings
from django.contrib.sites.models import Site

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import create_engine

from daiquiri import __version__ as daiquiri_version
from daiquiri.core.pgsphere import (
    ADQL_GEOMETRIES,
    PGSPHERE_TYPES,
    convert_geometry_to_adql,
    process_result_columns,
)
from daiquiri.core.utils import is_adql

logger = logging.getLogger(__name__)

VOTABLE_PLAIN_DATATYPES = frozenset({
    'boolean',
    'unsignedByte',
    'short',
    'int',
    'long',
    'float',
    'double'
})
VOTABLE_TEXT_DATATYPES = frozenset({
    'char'
})
VOTABLE_ARRAY_DATATYPES = frozenset({
    'boolean[]',
    'char[]',
    'short[]',
    'int[]',
    'long[]',
    'float[]',
    'double[]'
})

VOTABLE_DATATYPES = VOTABLE_PLAIN_DATATYPES | VOTABLE_TEXT_DATATYPES | VOTABLE_ARRAY_DATATYPES
INTEGER_NULLS = {
    'short': -32768,
    'int': -2147483648,
    'long': -9223372036854775808,
}
INTEGER_ARRAY_NULLS = {f'{datatype}[]': value for datatype, value in INTEGER_NULLS.items()}


class IntegerNullCollision(ValueError):
    pass


def generate_csv(generator, fields):
    # write header
    f = io.StringIO()
    csv.writer(f, quotechar='"').writerow([field['name'] for field in fields])
    yield f.getvalue()

    for row in generator:
        if row:
            # convert curl brace to square brace in all array-like columns
            corrected_row = []
            for col, field in zip(row, fields, strict=True):
                corrected_col = col

                if isinstance(col, str) and field.get('datatype') not in PGSPHERE_TYPES:
                    if col.startswith('{') and col.endswith('}'):
                        corrected_col = col.replace('{', '[').replace('}', ']')

                corrected_row = [*corrected_row, corrected_col]

            f = io.StringIO()
            csv.writer(f, quotechar='"').writerow(corrected_row)

            yield f.getvalue()


def correct_col_for_votable(col, datatype=None):
    if datatype in PGSPHERE_TYPES:
        return col

    corrected_col = col

    if col.startswith('{') and col.endswith('}'):  # this is an array
        # remove {} and replace , with space
        corrected_col = col.replace('{', '').replace('}', '').replace(',', ' ')

    if col.startswith('[') and col.endswith(']'):  # this is an array
        # remove {} and replace , with space
        corrected_col = col.replace('[', '').replace(']', '').replace(',', ' ')

    return corrected_col


def _integer_value(value, null_value, name, row_number):
    if isinstance(value, str):
        value = value.strip()
    if value is None or value == 'NULL':
        return null_value
    value = int(value)
    if value == null_value:
        raise IntegerNullCollision(
            f"Row {row_number}, column '{name}': {value} is reserved for NULL."
        )
    return value


def _votable_integer_array(value, datatype, name, row_number):
    if isinstance(value, str):
        value = value.strip('{}[]').replace('{', '').replace('}', '')
        value = value.split(',') if value else []

    null_value = INTEGER_ARRAY_NULLS[datatype]

    def items(array):
        for item in array:
            if isinstance(item, (list, tuple)):
                yield from items(item)
            else:
                yield str(_integer_value(item, null_value, name, row_number))

    return ' '.join(items(value))


def generate_votable(generator, fields, infos=[], links=[], services=[], table=None, empty=False, max_records=None, on_error=None):
    yield """<?xml version="1.0"?>
<VOTABLE version="1.3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://www.ivoa.net/xml/VOTable/v1.3"
    xmlns:stc="http://www.ivoa.net/xml/STC/v1.30">"""

    yield """
    <RESOURCE type="results">"""

    for title, content_role, href in links:
        yield f"""
        <LINK title={quoteattr(title)} content-role={quoteattr(content_role)} href={quoteattr(href)}/>"""  # noqa: E501

    for key, value in infos:
        if value is not None:
            yield f"""
        <INFO name={quoteattr(key)} value={quoteattr(value)} />"""

    if table is not None:
        yield f'''
        <TABLE name="{table}">'''
    else:
        yield """
        <TABLE>"""

    for field in fields:
        if field.get('datatype') in PGSPHERE_TYPES:
            field = dict(field, datatype='char', arraysize=None, xtype=field['datatype'])
        attrs = []
        for key in ['name', 'unit', 'ucd', 'utype', 'xtype']:
            if field.get(key):
                value = (
                    field[key]
                    .replace('&', '&amp;')
                    .replace('"', '&quot;')
                    .replace("'", '&apos;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                )
                if value in settings.RESERVED_COLNAMES:
                    value = f'&quot;{value}&quot;'

                attrs.append(f'{key}="{value}"')

        if field.get('datalink_id'):
            attrs.append(f'ID={quoteattr(field["datalink_id"])}')
        elif field.get('ucd'):
            if 'meta.id' in field['ucd'] and 'meta.ref' in field['ucd']:
                attrs.append('ID="datalinkID"')

        if 'arraysize' in field and not (field.get('datatype') or '').endswith('[]'):
            if field.get('datatype') == 'char' and field['arraysize'] is None:
                attrs.append('arraysize="*"')
            elif field['arraysize']:
                attrs.append('arraysize="{}"'.format(field['arraysize']))

        if 'datatype' in field:
            if field['datatype'] in VOTABLE_DATATYPES:
                if field['datatype'] in VOTABLE_ARRAY_DATATYPES:
                    attrs.append(f'datatype="{field["datatype"].rstrip("[]")}"')
                    if field['arraysize']:
                        attrs.append(f'arraysize="{field["arraysize"]}"')
                    else:
                        attrs.append('arraysize="*"')
                else:
                    attrs.append('datatype="{}"'.format(field['datatype']))
            elif not field.get('xtype'):
                attrs.append('xtype="{}"'.format(field['datatype']))

        if attrs:
            description = field.get('description')
            null_value = INTEGER_ARRAY_NULLS.get(field.get('datatype'))
            if description or null_value is not None:
                elements = []
                if description:
                    elements.append(f'<DESCRIPTION>{escape(description)}</DESCRIPTION>')
                if null_value is not None:
                    elements.append(f'<VALUES null={quoteattr(str(null_value))} />')
                yield """
                <FIELD {}> {} </FIELD>""".format(' '.join(attrs), ' '.join(elements))
            else:
                yield """
                <FIELD {} />""".format(' '.join(attrs))

    # fmt: off
    overflow = False
    error = None
    if not empty:
        yield """
            <DATA>
                <TABLEDATA>"""

        # write rows of the table yielded by the generator
        for i, row in enumerate(generator):
            if max_records is not None and  i >= max_records:
                overflow = True
                break
            try:
                cells = []
                for cell, field in zip(row, fields, strict=True):
                    datatype = field.get('datatype')
                    if cell in ['NULL', None]:
                        cells.append('')
                    elif datatype in VOTABLE_PLAIN_DATATYPES:
                        cells.append(str(cell))
                    elif datatype in INTEGER_ARRAY_NULLS:
                        cells.append(_votable_integer_array(cell, datatype, field['name'], i + 1))
                    else:
                        cells.append(correct_col_for_votable(escape(str(cell)), datatype))
            except IntegerNullCollision as exc:
                error = str(exc)
                if on_error:
                    on_error(error)
                break
            yield '<TR><TD>{}</TD></TR>'.format('</TD><TD>'.join(cells))

        yield """
                </TABLEDATA>
            </DATA>"""

    yield """
        </TABLE>"""

    if error:
        yield f"""
        <INFO name={quoteattr('QUERY_STATUS')} value={quoteattr('ERROR')}>{escape(error)}</INFO>"""
    elif overflow:
        yield f"""
        <INFO name={quoteattr('QUERY_STATUS')} value={quoteattr('OVERFLOW')} />"""

    yield """
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


def _is_array_datatype(datatype):
    return bool(datatype and datatype.endswith('[]'))


def generate_fits(generator, fields, nrows, table_name=None, array_infos={}):
    if any(_is_array_datatype(field.get('datatype')) for field in fields):
        with tempfile.TemporaryFile() as rows_file, tempfile.TemporaryFile() as heap_file:
            yield from _generate_fits(
                generator, fields, nrows, table_name, array_infos, rows_file, heap_file
            )
    else:
        yield from _generate_fits(generator, fields, nrows, table_name, array_infos)


def _generate_fits(
    generator, fields, nrows, table_name, field_widths, rows_file=None, heap_file=None
):
    DEFAULT_CHAR_SIZE = 256

    # VO format label, FITS format label, size in bytes, NULL value, encoded value
    # fmt:off
    formats_dict = {
        'boolean':   ('s', 'L', 1,  b'\x00',             lambda x: b'T' if x == 'true' else b'F'), #noqa: E501
        'short':     ('h', 'I', 2,  INTEGER_NULLS['short'], int),
        'int':       ('i', 'J', 4,  INTEGER_NULLS['int'],   int),
        'long':      ('q', 'K', 8,  INTEGER_NULLS['long'],  int),
        'float':     ('f', 'E', 4,  float('nan'),        float),
        'double':    ('d', 'D', 8,  float('nan'),        float),
        'char':      ('s', 'A', 32, b'',                 lambda x: x.encode()),
        'timestamp': ('s', 'A', 19, b'',                 lambda x: x.encode()),
        'array':     ('s', 'A', 64, b'',                 lambda x: x.encode()),
        'unknown':   ('s', 'A', 8,  b'',                 lambda x: x.encode()),
        'boolean[]': ('s', 'L', 1,  b'\x00',             lambda x: b'T' if str(x).lower() in ('t', 'true') else b'F'), # noqa: E501
        'short[]':   ('h', 'I', 2,  INTEGER_ARRAY_NULLS['short[]'], int),
        'int[]':     ('i', 'J', 4,  INTEGER_ARRAY_NULLS['int[]'],   int),
        'long[]':    ('q', 'K', 8,  INTEGER_ARRAY_NULLS['long[]'],  int),
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
        if datatype in PGSPHERE_TYPES:
            datatypes[i] = 'char'
            arraysizes[i] = field_widths.get(names[i], DEFAULT_CHAR_SIZE)
        elif datatype == 'timestamp':
            arraysizes[i] = formats_dict['timestamp'][2]
        elif datatype in ('char', 'array') and arraysize == '':
            arraysizes[i] = DEFAULT_CHAR_SIZE
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

    # Q descriptors occupy 16 bytes.
    naxis1 = sum(
        16 if _is_array_datatype(datatype) else (arraysize or formats_dict[datatype][2])
        for datatype, arraysize in zip(datatypes, arraysizes)
    )
    if rows_file is not None:
        naxis2, pcount = _stage_fits_rows(
            generator, datatypes, arraysizes, formats_dict, rows_file, heap_file
        )
        if rows_file.tell() != naxis1 * naxis2:
            raise ValueError('FITS row size does not match NAXIS1')
    else:
        naxis2, pcount = nrows, 0
    tfields = len(names)

    logo = get_daiquiri_logo(str(Site.objects.get_current())[:30], daiquiri_version)

    # Main header #############################################################
    simple_card = "SIMPLE  =                    T / conforms to FITS standard                      "

    # fmt:off
    header0info = [
        ('BITPIX',  '8',       'array data type'),
        ('NAXIS',   '1',       'number of array dimensions'),
        ('NAXIS1',  '2880',    'number of characters'),
        ('EXTEND',  'T',       ''),
        ('NTABLE',  '1',       ''),
        ('LONGSTRN',"'OGIP 1.0'",'The OGIP long string convention may be used.'),
        ('COMMENT', 'This FITS file may contain long string keyword values that are',''),
        ('COMMENT', 'continued over multiple keywords.  This convention uses the  "&"',''),
        ('COMMENT', 'character at the end of a string which is then continued', ''),
        ('COMMENT', 'on subsequent keywords whose name = "CONTINUE".', ''),
        ('END',     '',        ''),
    ]
    # fmt:on

    h0 = simple_card + ''.join([create_fits_card(*entry) for entry in header0info])
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
        ('PCOUNT',   f'{pcount}',  'number of group parameters    '),
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
        if not _is_array_datatype(datatype):
            format_str = (str(arraysize) + formats_dict[datatype][1]).ljust(8)
        else:
            format_str = '1Q' + formats_dict[datatype][1]

        h1 += create_fits_card(f'TTYPE{i + 1}', f"'{name.ljust(8)}'", f'label for col {i + 1}    ')
        h1 += create_fits_card(f'TFORM{i + 1}', f"'{format_str}'", f'format for col {i + 1}    ')

        # NULL values only for int-like types
        if datatype in INTEGER_NULLS or datatype in INTEGER_ARRAY_NULLS:
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
    h1 += ' ' * (-len(h1) % 2880)

    yield h1.encode()

    # Data ####################################################################
    if rows_file is not None:
        for staged_file in (rows_file, heap_file):
            staged_file.seek(0)
            while chunk := staged_file.read(65536):
                yield chunk
        data_size = naxis1 * naxis2 + pcount
    else:
        fmt = '>' + ''.join(
            str(arraysize) + formats_dict[datatype][0]
            for datatype, arraysize in zip(datatypes, arraysizes)
        )
        row_count = 0
        for row in generator:
            encoded_row = []
            for value, datatype in zip(row, datatypes):
                if value is None or value == 'NULL':
                    encoded = formats_dict[datatype][3]
                else:
                    encoded = formats_dict[datatype][4](value)
                encoded_row.append(encoded)
            yield struct.pack(fmt, *encoded_row)
            row_count += 1
        data_size = naxis1 * row_count

    padding = -data_size % 2880
    if padding:
        yield b'\x00' * padding


def _stage_fits_rows(generator, datatypes, arraysizes, formats_dict, rows_file, heap_file):
    row_count = 0
    for row in generator:
        row_data = bytearray()
        for value, datatype, arraysize in zip(row, datatypes, arraysizes):
            if _is_array_datatype(datatype):
                element_count, payload = _encode_fits_array(value, datatype, formats_dict)
                heap_offset = heap_file.tell() if element_count else 0
                heap_file.write(payload)
                row_data.extend(struct.pack('>qq', element_count, heap_offset))
            else:
                if value is None or value == 'NULL':
                    encoded = formats_dict[datatype][3]
                else:
                    encoded = formats_dict[datatype][4](value)
                scalar_fmt = '>' + str(arraysize) + formats_dict[datatype][0]
                row_data.extend(struct.pack(scalar_fmt, encoded))
        rows_file.write(row_data)
        row_count += 1
    return row_count, heap_file.tell()


def _encode_fits_array(value, datatype, formats_dict):
    values = parse_fits_array(value, datatype)
    if datatype in ('char[]', 'boolean[]'):
        if any(item is None or item == 'NULL' for item in values):
            raise ValueError(f'NULL elements in FITS {datatype} columns are not supported')
        payload = b''.join(formats_dict[datatype][4](item) for item in values)
        return (len(payload) if datatype == 'char[]' else len(values)), payload

    encoded = []
    for item in values:
        if item is None or item == 'NULL':
            encoded.append(formats_dict[datatype][3])
        else:
            encoded.append(formats_dict[datatype][4](item))
    if encoded:
        payload = struct.pack('>' + str(len(encoded)) + formats_dict[datatype][0], *encoded)
    else:
        payload = b''
    return len(encoded), payload


def create_fits_card(key: str, val: str, comment: str) -> str:
    key_length = 8
    line_length = 80
    value_text = str(val)
    value_length = line_length - key_length - len(comment)
    line = key[:key_length].ljust(key_length)

    needs_tcomm_quotes = ("TCOMM" in key and value_text != "" and not value_text.startswith("'"))
    total_size = 15 + len(comment) + len(value_text) + (2 if needs_tcomm_quotes else 0)

    lines = []

    if not total_size > line_length:
        if val != '':
            if needs_tcomm_quotes:
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


def parse_fits_array(obj_str: str | list | tuple | None, obj_type: str) -> list:
    if obj_str is None or obj_str == 'NULL' or obj_str == '{}':
        return []
    if isinstance(obj_str, list | tuple):
        return list(obj_str)

    array = obj_str.strip('{}').split(',')
    if obj_type == 'char[]':
        array = [f'{item}_' for item in array[:-1]] + [array[-1]]
    return array


def generate_parquet(
    schema_name: str,
    table_name: str,
    fields: dict,
    metadata: str,
    database_config: dict,
    query_language=None,
    on_row_count=None,
):
    native_fields = fields
    fields = process_result_columns(fields, query_language)
    PQ_TYPE_MAP = {
        'boolean': pa.bool_(),
        'short': pa.int16(),
        'int': pa.int32(),
        'long': pa.int64(),
        'float': pa.float32(),
        'double': pa.float64(),
        'boolean[]': pa.list_(pa.bool_()),
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
        datatype = PQ_TYPE_MAP.get(f['datatype'], pa.string())
        arrow_fields.append(pa.field(f['name'], datatype))
    schema = pa.schema(arrow_fields)

    sink = YieldingWriter()
    buffer = pa.PythonFile(sink)
    writer = pq.ParquetWriter(buffer, schema, compression='zstd')

    kv_meta = {
        b'IVOA.VOTable-Parquet.version': b'1.0',
        b'IVOA.VOTable-Parquet.content': metadata.encode('utf-8'),
    }
    writer.add_key_value_metadata(kv_meta)

    processed_rows = 0
    try:
        for chunk in pd.read_sql(query, con=connection, chunksize=10000):
            if is_adql(query_language):
                for field in native_fields:
                    datatype = field['datatype']
                    if datatype in ADQL_GEOMETRIES:
                        chunk[field['name']] = chunk[field['name']].map(
                            lambda value, datatype=datatype: convert_geometry_to_adql(
                                value, datatype
                            )
                        )
            table = pa.Table.from_pandas(chunk, preserve_index=False).cast(schema)
            writer.write_table(table)
            if on_row_count:
                processed_rows += len(chunk)
                on_row_count(processed_rows)

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
