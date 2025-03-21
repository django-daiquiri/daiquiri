import csv
import datetime
import io
import struct
import sys
from xml.sax.saxutils import escape, quoteattr

from django.contrib.sites.models import Site

from daiquiri import __version__ as daiquiri_version


def generate_csv(generator, fields):
    if sys.version_info.major >= 3:
        io_class = io.StringIO
    else:
        io_class = io.BytesIO

    # write header
    f = io_class()
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

            f = io_class()
            csv.writer(f, quotechar='"').writerow(corrected_row)
            yield f.getvalue()


def correct_col_for_votable(col):
    corrected_col = col

    if col.startswith('{') and col.endswith('}'): # this is an array
        # remove {} and replace , with space
        corrected_col = col.replace('{', '').replace('}', '').replace(',', ' ')

    return corrected_col

def generate_votable(generator, fields, infos=[], links=[], services=[], table=None, empty=None):
    yield '''<?xml version="1.0"?>
<VOTABLE version="1.3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://www.ivoa.net/xml/VOTable/v1.3"
    xmlns:stc="http://www.ivoa.net/xml/STC/v1.30">'''

    yield '''
    <RESOURCE type="results">'''

    for key, value in infos:
        if value is not None:
            yield f'''
            <INFO name={quoteattr(key)} value={quoteattr(value)} />'''

    for title, content_role, href in links:
        yield f'''
        <LINK title={quoteattr(title)} content-role={quoteattr(content_role)} href={quoteattr(href)}/>'''

    if table is not None:
        yield f'''
        <TABLE name="{table}">'''
    else:
        yield '''
        <TABLE>'''

    for field in fields:
        attrs = []
        for key in ['name', 'unit', 'ucd', 'utype']:
            if field.get(key):
                value = field[key].replace('&', '&amp;') \
                                  .replace('"', '&quot;') \
                                  .replace("'", '&apos;') \
                                  .replace('<', '&lt;') \
                                  .replace('>', '&gt;')
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
            if field['datatype'] in ['boolean', 'char', 'unsignedByte', 'short', 'int', 'long', 'float', 'double']:
                attrs.append('datatype="{}"'.format(field['datatype']))
            else:
                attrs.append('xtype="{}"'.format(field['datatype']))

        if attrs:
            yield '''
            <FIELD {} />'''.format(' '.join(attrs))

    if not empty:
        yield '''
            <DATA>
                <TABLEDATA>'''

        # write rows of the table yielded by the generator
        for row in generator:
            yield '''
                    <TR>
                        <TD>{}</TD>
                    </TR>'''.format('''</TD>
                        <TD>'''.join([
                            ('' if cell in ['NULL', None] else correct_col_for_votable(escape(str(cell))))
                            for cell in row
                        ]))

        yield '''
                </TABLEDATA>
            </DATA>'''
    yield '''
        </TABLE>
    </RESOURCE>'''

    for service in services:
        yield '''
    <RESOURCE type="meta" utype="adhoc:service">'''
        for param in service.get('params', []):
            yield '''
        <PARAM name="{name}" datatype="{datatype}" arraysize="{arraysize}" value="{value}" />'''.format(**param)

        for group in service.get('groups', []):
            yield '''
        <GROUP name="{name}">'''.format(**group)
            for param in group.get('params', []):
                yield '''
            <PARAM name="{name}" datatype="{datatype}" arraysize="{arraysize}" value="{value}" ref="{ref}"/>'''.format(**param)  # noqa: E501
            yield '''
        </GROUP>'''
        yield '''
    </RESOURCE>'''
    yield '''
</VOTABLE>
'''


def generate_fits(generator, fields, nrows, table_name=None):

    # VO format label, FITS format label, size, NULL value, encoded value
    formats_dict = {
        'boolean':      ('s', 'L', 1,  b'\x00',             lambda x: b'T' if x == 'true' else b'F'),
        'short':        ('h', 'I', 2,  32767,               int),
        'int':          ('i', 'J', 4,  2147483647,          int),
        'long':         ('q', 'K', 8,  9223372036854775807, int),
        'float':        ('f', 'E', 4,  float('nan'),        float),
        'double':       ('d', 'D', 8,  float('nan'),        float),
        'char':         ('s', 'A', 32, b'',                 lambda x: x.encode()),
        'timestamp':    ('s', 'A', 19, b'',                 lambda x: x.encode()),
        'array':        ('s', 'A', 64, b'',                 lambda x: x.encode()),
        'spoint':       ('s', 'A', 64, b'',                 lambda x: x.encode()),
        'unknown':      ('s', 'A', 8,  b'',                 lambda x: x.encode())
    }

    names = [field['name'] for field in fields]
    datatypes = [field['datatype'] for field in fields]
    arraysizes = [field.get('arraysize') or '' for field in fields]

    for i, d in enumerate(zip(datatypes, arraysizes)):
        if d[0] == 'timestamp':
            arraysizes[i] = formats_dict['timestamp'][2]
        elif d[0] in ('char', 'spoint', 'array') and d[1] == '':
            arraysizes[i] = formats_dict[d[0]][2]
        elif d[0] is None:
            datatypes[i] = 'unknown'
            arraysizes[i] = formats_dict['unknown'][2]

    units = []
    ucds = []
    for d in fields:
        if 'unit' in d and d['unit'] is not None:
            units.append(d['unit'])
        else:
            units.append('')
        if 'ucd' in d and d['ucd'] is not None:
            ucds.append(d['ucd'])
        else:
            ucds.append('')

    naxis1 = sum([formats_dict[i[0]][2] if not i[1] else i[1]
                  for i in zip(datatypes, arraysizes)])
    naxis2 = nrows
    tfields = len(names)

    site = str(Site.objects.get_current())[:30]

    content = """

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
                    \\\\               v%s//
                      \\\\%s//
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

    """.replace('\x0a', ' ') % (daiquiri_version.ljust(18),
           (' ' * (15 - len(site) // 2) + site).ljust(30))

    # Main header #############################################################
    header0 = [i.ljust(80) for i in [
        'SIMPLE  =                    T / conforms to FITS standard',
        'BITPIX  =                    8 / array data type',
        'NAXIS   =                    1 / number of array dimensions',
        'NAXIS1  =                 2880 / number of characters',
        'EXTEND  =                    T',
        'NTABLE  =                    1',
        'END'
        ]]

    h0 = ''.join(header0)
    h0 += ' ' * (2880 * (len(h0) // 2880 + 1) - len(h0))

    yield h0.encode()

    # Main table content - required by some FITS viewers ######################

    yield (content + '\x00' * (2880 - len(content))).encode()

    # Table header ############################################################
    header1 = [
       "XTENSION= 'BINTABLE'           / binary table extension".ljust(80),
       'BITPIX  =                    8 / array data type'.ljust(80),
       'NAXIS   =                    2 / number of array dimensions'.ljust(80),
       'NAXIS1  = %20d / length of dimension 1'.ljust(64),
       'NAXIS2  = %20d / length of dimension 2'.ljust(64),
       'PCOUNT  =                    0 / number of group parameters'.ljust(80),
       'GCOUNT  =                    1 / number of groups'.ljust(80),
       'TFIELDS = %20d / number of table fields'.ljust(64),
        ]
    if table_name is not None:
        # table_name needs to be shorter than 68 chars
        header1.append((f"EXTNAME = '{table_name[:68]!s}' / table name").ljust(80))

    h1 = ''.join(header1) % (naxis1, naxis2, tfields)

    ttype = ("TTYPE%s", "= '%s'")
    tform = ("TFORM%s", "= '%s'")
    tnull = ("TNULL%s", "=  %s")
    tunit = ("TUNIT%s", "= '%s'")
    tucd = ("TUCD%s", "= '%s'")

    for i, d in enumerate(zip(names, datatypes, arraysizes, units, ucds)):
        temp = "".join(((ttype[0] % str(i + 1)).ljust(8),
                       ttype[1] % d[0][:68].ljust(8)))[:80].ljust(30)
        temp += ' / label for column %d' % (i + 1)
        temp = temp[:80]
        temp += ' ' * (80 - len(temp))
        h1 += temp

        ff = (str(d[2]) + formats_dict[d[1]][1]).ljust(8)
        temp = "".join(((tform[0] % str(i + 1)).ljust(8),
                       tform[1] % ff))[:80].ljust(31)
        temp += '/ format for column %d' % (i + 1)
        temp = temp[:80]
        temp += ' ' * (80 - len(temp))
        h1 += temp

        # NULL values only for int-like types
        if d[1] in ('short', 'int', 'long'):
            temp = "".join(((tnull[0] % str(i + 1)).ljust(8),
                           tnull[1] % formats_dict[d[1]][3]))[:80].ljust(31)
            temp += '/ blank value for column %d' % (i + 1)
            temp = temp[:80]
            temp += ' ' * (80 - len(temp))
            h1 += temp

        if d[3]:
            temp = "".join(((tunit[0] % str(i + 1)).ljust(8),
                           tunit[1] % d[3][:68].ljust(8)))[:80].ljust(30)
            temp += ' / unit for column %d' % (i + 1)
            temp = temp[:80]
            temp += ' ' * (80 - len(temp))
            h1 += temp

        if d[4]:
            temp = "".join(((tucd[0] % str(i + 1)).ljust(8),
                           tucd[1] % d[4][:68].ljust(8)))[:80].ljust(30)
            temp += ' / ucd for column %d' % (i + 1)
            temp = temp[:80]
            temp += ' ' * (80 - len(temp))
            h1 += temp

    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    h1 += (f"DATE-HDU= '{now}' / UTC date of HDU creation").ljust(80)

    h1 += 'END'.ljust(80)
    h1 += ' ' * (2880 * (len(h1) // 2880 + 1) - len(h1))

    yield h1.encode()

    # Data ####################################################################
    fmt = '>' + ''.join([str(i[1]) + formats_dict[i[0]][0]
                         for i in zip(datatypes, arraysizes)])

    row_count = 0
    for row in generator:
        r = [formats_dict[i[1]][3] if i[0] == 'NULL'
             else formats_dict[i[1]][4](i[0]) for i in zip(row, datatypes)]

        yield struct.pack(fmt, *r)
        row_count += 1

    # Footer padding (to fill the last block to 2880 bytes) ###################
    ln = naxis1 * row_count
    footer = '\x00' * (2880 * (ln // 2880 + 1) - ln)

    yield footer.encode()
