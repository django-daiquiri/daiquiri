import pytest

from django.urls import reverse

users = (
    ('admin', 'admin'),
    ('manager', 'manager'),
    ('user', 'user'),
    ('anonymous', None),
)

status_map = {
    'html': {
        'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 302
    },
    'html_a': {
        'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 302
    },
    'html_a_a': {
        'admin': 403, 'manager': 200, 'user': 403, 'anonymous': 302
    },
    'html_a_b': {
        'admin': 404, 'manager': 404, 'user': 404, 'anonymous': 404
    }
}


@pytest.mark.parametrize(('username', 'password'), users)
def test_html(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('files:file', kwargs={
        'file_path': 'html/'
    })
    response = client.get(url)
    assert response.status_code == status_map['html'][username]


@pytest.mark.parametrize(('username', 'password'), users)
def test_html_a(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('files:file', kwargs={
        'file_path': 'html/a/'
    })
    response = client.get(url)
    assert response.status_code == status_map['html_a'][username]


@pytest.mark.parametrize(('username', 'password'), users)
def test_html_a_a(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('files:file', kwargs={
        'file_path': 'html/a/a/'
    })
    response = client.get(url)
    assert response.status_code == status_map['html_a_a'][username]


@pytest.mark.parametrize(('username', 'password'), users)
def test_html_a_b(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('files:file', kwargs={
        'file_path': 'html/a/b/'
    })
    response = client.get(url)
    assert response.status_code == status_map['html_a_b'][username]
