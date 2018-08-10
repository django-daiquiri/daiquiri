import csv
import io
import sys
import struct


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
            f = io_class()
            csv.writer(f, quotechar='"').writerow(row)
            yield f.getvalue()


def generate_votable(generator, fields, resource_name=None, table_name=None, links=None, query_status=None, empty=None):

        yield '''<?xml version="1.0"?>
<VOTABLE version="1.3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://www.ivoa.net/xml/VOTable/v1.3"
    xmlns:stc="http://www.ivoa.net/xml/STC/v1.30">'''

        if resource_name:
            yield '''
    <RESOURCE name="%(name)s" type="results">''' % {'name': resource_name}
        else:
            yield '''
    <RESOURCE type="results">'''

        if query_status == 'OK':
            yield '''
        <INFO name="QUERY_STATUS" value="OK" />'''
        elif query_status == 'OVERFLOW':
            yield '''
        <INFO name="QUERY_STATUS" value="OVERFLOW" />'''

        if links:
            for link in links:
                attrs = []
                for key in ['name', 'href', 'content-type', 'content-role']:
                    if key in link and link[key]:
                        attrs.append('%s="%s"' % (key, link[key]))

                yield '''
        <LINK %s />''' % ' '.join(attrs)

        if table_name:
            yield '''
        <TABLE name="%(table)s">''' % {'table': table_name}
        else:
            yield '''
        <TABLE>'''

        for field in fields:
            attrs = []
            for key in ['name', 'unit', 'ucd', 'utype']:
                if key in field and field[key]:
                    value = field[key].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    attrs.append('%s="%s"' % (key, value))

            if 'arraysize' in field and field['arraysize']:
                attrs.append('arraysize="%d"' % field['arraysize'])

            if field['datatype'] in ['char', 'unsignedByte', 'short', 'int', 'long', 'float', 'double']:
                attrs.append('datatype="%s"' % field['datatype'])
            else:
                attrs.append('xtype="%s"' % field['datatype'])

            yield '''
            <FIELD %s />''' % ' '.join(attrs)

        if not empty:
            yield '''
            <DATA>
                <TABLEDATA>'''

            # write rows of the table yielded by the generator
            for row in generator:
                yield '''
                    <TR>
                        <TD>%s</TD>
                    </TR>''' % '''</TD>
                        <TD>'''.join([('' if cell == 'NULL' else str(cell)) for cell in row])

            yield '''
                </TABLEDATA>
            </DATA>'''
        yield '''
        </TABLE>
    </RESOURCE>
</VOTABLE>
'''


def generate_fits(generator, fields, nrows, table_name=None):

    # VO format label, FITS format label, size, NULL value
    formats_dict = {
        'char': ('s', 'A', 1, ''.encode),
        'unsignedByte': ('B', 'B', 1, 255),
        'short': ('h', 'I', 2, 32767),
        'int': ('i', 'J', 4, 2147483647),
        'long': ('q', 'K', 8, 9223372036854775807),
        'float': ('f', 'E', 4, float('nan')),
        'double': ('d', 'D', 8, float('nan')),
        'spoint': ('s', 'A', 64, ''.encode())
    }

    names = [d['name'] for d in fields]
    datatypes = [d['datatype'] for d in fields]
    arraysizes = [d['arraysize'] if d['arraysize'] is not None else ''
                  for d in fields]

    naxis1 = sum([formats_dict[i[0]][2] if not i[1] else i[1]
                  for i in zip(datatypes, arraysizes)])
    naxis2 = nrows
    tfields = len(names)

    # Main header
    header0 = [i.ljust(80) for i in [
        'SIMPLE  =                    T / conforms to FITS standard',
        'BITPIX  =                    8 / array data type',
        'NAXIS   =                    0 / number of array dimensions',
        'EXTEND  =                    T',
        'END'
        ]]

    h0 = ''.join(header0)
    h0 += ' ' * (2880 * (len(h0) // 2880 + 1) - len(h0))

    yield h0.encode()

    # Table header
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
        header1.append(("EXTNAME = '%s'" % str(table_name[:68])).ljust(80))

    h1 = ''.join(header1) % (naxis1, naxis2, tfields)

    ttype = "TTYPE%s = '%s'"
    tform = "TFORM%s = '%s'"
    tnull = "TNULL%s = %s"

    for i, d in enumerate(zip(names, datatypes, arraysizes)):
        temp = (ttype % (str(i + 1).ljust(2), d[0].ljust(8)))[:80]
        temp += ' ' * (80 - len(temp))
        h1 += temp

        ff = (str(d[2]) + formats_dict[d[1]][1]).ljust(8)
        temp = (tform % (str(i + 1).ljust(2), ff))[:80]
        temp += ' ' * (80 - len(temp))
        h1 += temp

        # NULL values only for int like types
        if d[1] in ('unsignedByte', 'short', 'int', 'long'):
            temp = (tnull % (str(i + 1).ljust(2), formats_dict[d[1]][3]))[:80]
            temp += ' ' * (80 - len(temp))
            h1 += temp

    h1 += 'END'.ljust(80)
    h1 += ' ' * (2880 * (len(h1) // 2880 + 1) - len(h1))

    yield h1.encode()

    # Table data
    conversions = [[], [], []]
    for i, x in enumerate(datatypes):
        if x in ('unsignedByte', 'short', 'int', 'long'):
            conversions[0].append(i)
        elif x in ('float', 'double'):
            conversions[1].append(i)
        else:
            # The rest are strings and we store their location so we only
            # encode (to bytes) these columns and not waste the energy
            conversions[2].append(i)

    fmt = '>' + ''.join([str(i[1]) + formats_dict[i[0]][0]
                         for i in zip(datatypes, arraysizes)])

    row_count = 0
    for row in generator:
        for i in conversions[0]:
            row[i] = int(row[i])
        for i in conversions[1]:
            row[i] = float(row[i])
        for i in conversions[2]:
            row[i] = row[i].encode()

        yield struct.pack(fmt, *row)
        row_count += 1

    # Footer padding
    ln = naxis1 * row_count
    footer = ' ' * (2880 * (ln // 2880 + 1) - ln)

    yield footer.encode()
