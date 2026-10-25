import xml.etree.ElementTree as et

from daiquiri.core.generators import generate_votable


votable_ns = '{http://www.ivoa.net/xml/VOTable/v1.3}'
fields = [{'name': 'values_int', 'datatype': 'int[]', 'arraysize': None}]


def test_votable_integer_array_nulls():
    rows = [('{1,NULL,3}',), ('{1,2,3}',), ('{}',), (None,)]
    root = et.fromstring(''.join(generate_votable(rows, fields)))

    null = root.find(f'.//{votable_ns}FIELD/{votable_ns}VALUES')
    values = root.findall(f'.//{votable_ns}TR/{votable_ns}TD')

    assert null.attrib['null'] == '-2147483648'
    assert [value.text or '' for value in values] == [
        '1 -2147483648 3', '1 2 3', '', ''
    ]


def test_votable_integer_array_null_collision():
    rows = [('{1,NULL,3}',), ('{-2147483648,2}',), ('{4,5}',)]
    root = et.fromstring(''.join(generate_votable(rows, fields)))

    values = root.findall(f'.//{votable_ns}TR/{votable_ns}TD')
    error = root.find(f'.//{votable_ns}INFO[@name="QUERY_STATUS"][@value="ERROR"]')

    assert [value.text for value in values] == ['1 -2147483648 3']
    assert error is not None
