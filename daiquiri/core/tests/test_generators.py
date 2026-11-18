import xml.etree.ElementTree as et

from daiquiri.core.generators import (
    flatten_array,
    flatten_array_rows,
    generate_csv,
    generate_votable,
    parse_fits_array,
)


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


def test_flatten_matrix_like_one_dimensional_array():
    row = ('{{1,2},{3,4}}',)
    root = et.fromstring(''.join(generate_votable(flatten_array_rows([row], fields), fields)))
    value = root.find(f'.//{votable_ns}TR/{votable_ns}TD')
    field = root.find(f'.//{votable_ns}FIELD')

    assert value.text == '1 2 3 4'
    assert field.attrib['arraysize'] == '*'
    assert '"[1,2,3,4]"' in ''.join(generate_csv(flatten_array_rows([row], fields), fields))
    flat_row = next(flatten_array_rows([row], fields))
    assert parse_fits_array(flat_row[0], 'int[]') == ['1', '2', '3', '4']
    assert flatten_array([[1, 2], [3, 4]]) == [1, 2, 3, 4]


def test_flatten_numeric_matrix_elements():
    assert flatten_array('{{1,NULL},{NaN,-2.5}}') == '{1,NULL,NaN,-2.5}'
    assert flatten_array('{1,2}') == '{1,2}'


def test_flatten_array_rows_keeps_other_values():
    fields = [
        {'name': 'value', 'datatype': 'int[]'},
        {'name': 'flags', 'datatype': 'boolean[]'},
        {'name': 'text', 'datatype': 'char[]'},
    ]
    rows = [
        ([[1, 2], [3, 4]], [[True, False]], [['a', 'b']]),
        ([1, 2], None, None),
    ]

    assert list(flatten_array_rows(rows, fields)) == [
        [[1, 2, 3, 4], [[True, False]], [['a', 'b']]],
        [[1, 2], None, None],
    ]
