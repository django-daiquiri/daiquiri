import csv
import io
import sys


def generate_csv(generator):
    if sys.version_info.major >= 3:
        io_class = io.StringIO
    else:
        io_class = io.BytesIO

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
            for key in ['name', 'arraysize', 'unit', 'ucd', 'utype']:
                if key in field and field[key]:
                    attrs.append('%s="%s"' % (key, field[key]))

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
