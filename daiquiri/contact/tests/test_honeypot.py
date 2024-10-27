from django.conf import settings
from django.urls import reverse

from daiquiri.core.utils import sanitize_str

testset_login = {
    "url": "account_login",
    "data": {
        "login": "user",
        "password": "user",
    },
}


testset_signup = {
    "url": "account_signup",
    "data": {
        "email": "testing@example.com",
        "username": "testing",
        "first_name": "Tanja",
        "last_name": "Test",
        "password1": "testing",
        "password2": "testing"
    },
}

testset_contact = {
    "url": "contact:contact",
    "data": {"subject": "Test", "message": "This is a test."},
}


def run_honeypot_test(db, client, testset, honeypot, exp):
    data = testset["data"]
    url = reverse(testset["url"])
    if settings.HONEYPOT_ENABLED is False:
        exp = 302
        if "contact" in url:
            exp = 200
    if honeypot is not None:
        data[sanitize_str(settings.HONEYPOT_FIELD_NAME)] = honeypot

    response = client.post(url, data)
    assert response.status_code == exp


def test_contact_post(db, client):
    client.login(username="admin", password="admin")
    run_honeypot_test(db, client, testset_contact, settings.HONEYPOT_FIELD_VALUE, 200)


def test_contact_post_honeypot_field_invalid(db, client):
    client.login(username="admin", password="admin")
    run_honeypot_test(db, client, testset_contact, "some_text", 400)


def test_contact_post_honeypot_field_missing(db, client):
    client.login(username="admin", password="admin")
    run_honeypot_test(db, client, testset_contact, None, 400)
