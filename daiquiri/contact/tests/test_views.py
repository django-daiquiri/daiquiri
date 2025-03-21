import pytest

from django.urls import reverse

from ..models import ContactMessage

valid_users = (
    ('admin', 'admin'),
    ('manager', 'manager'),
    ('user', 'user'),
)

invalid_users = (
    ('anonymous', None),
)

users = valid_users + invalid_users

status_map = {
    'messages': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 302
    }
}


@pytest.mark.parametrize(('username', 'password'), users)
def test_messages(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('contact:messages')
    response = client.get(url)
    assert response.status_code == status_map['messages'][username]


@pytest.mark.parametrize(('username', 'password'), valid_users)
def test_contact_get(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('contact:contact')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(('username', 'password'), invalid_users)
def test_contact_get_anon(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('contact:contact')
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.parametrize(('username', 'password'), valid_users)
def test_contact_post(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('contact:contact')
    response = client.post(url, {
        'subject': 'Test',
        'message': 'This is a test.'
    })
    assert response.status_code == 200
    assert ContactMessage.objects.count() == 3


@pytest.mark.parametrize(('username', 'password'), valid_users)
def test_contact_post_invalid(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('contact:contact')
    response = client.post(url, {})
    assert response.status_code == 200
    assert ContactMessage.objects.count() == 2


@pytest.mark.parametrize(('username', 'password'), valid_users)
def test_contact_post_cancel(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('contact:contact')
    response = client.post(url, {
        'cancel': True
    })
    assert response.status_code == 200
    assert ContactMessage.objects.count() == 2
