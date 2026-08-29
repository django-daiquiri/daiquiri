import xml.etree.ElementTree as et

from django.test import override_settings
from django.urls import reverse
from django.utils.http import urlencode

from daiquiri.conesearch.tests.adapter import BoxConeSearchAdapter


url_names = {
    'search': 'conesearch:search'
}

adapter = 'daiquiri.conesearch.tests.adapter.BoxConeSearchAdapter'

resource = 'daiquiri_data_obs.stars'

resources = {
    resource: {
        'schema_name': 'daiquiri_data_obs',
        'table_name': 'stars',
        'column_names': ['id', 'ra', 'dec'],
        'coordinates_columns': {
            'RA': 'ra',
            'DEC': 'dec'
        },
    }
}

query = {
    'RA': 145.7,
    'DEC': -60.3,
    'SR': 1
}

votable_ns = '{http://www.ivoa.net/xml/VOTable/v1.3}'


@override_settings(
    CONESEARCH_ADAPTER=adapter,
    CONESEARCH_RESOURCES=resources
)
def test_search(db, client):
    '''
    A cone-search request returns a VOTable.
    '''
    client.login(username='user', password='user')

    url = reverse(url_names['search'], args=[resource]) + '?' + urlencode(query)
    response = client.get(url)

    assert response.status_code == 200


@override_settings(
    CONESEARCH_ADAPTER=adapter,
    CONESEARCH_ANONYMOUS=True,
    CONESEARCH_RESOURCES=resources
)
def test_search_anonymous(db, client):
    '''
    A cone-search request can be performed anonymously when enabled.
    '''
    url = reverse(url_names['search'], args=[resource]) + '?' + urlencode(query)
    response = client.get(url)

    assert response.status_code == 200


@override_settings(
    CONESEARCH_ADAPTER=adapter,
    CONESEARCH_RESOURCES=resources
)
def test_search_overflow(db, client, mocker):
    '''
    A truncated cone-search response reports an overflow.
    '''
    mocker.patch.object(BoxConeSearchAdapter, 'max_records', 1)

    client.login(username='user', password='user')

    url = reverse(url_names['search'], args=[resource]) + '?' + urlencode(query)
    response = client.get(url)

    assert response.status_code == 200

    root = et.fromstring(b''.join(response.streaming_content))
    rows = root.findall(f'.//{votable_ns}TR')
    overflow = root.find(
        f'.//{votable_ns}INFO[@name="QUERY_STATUS"][@value="OVERFLOW"]'
    )

    assert len(rows) == 1
    assert overflow is not None
