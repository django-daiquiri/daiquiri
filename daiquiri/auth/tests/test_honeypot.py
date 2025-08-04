from django.conf import settings
from django.urls import reverse

from daiquiri.core.utils import sanitize_str

testset_login = {
    'url': 'account_login',
    'data': {
        'login': 'user',
        'password': 'user',
    },
}


testset_signup = {
    'url': 'account_signup',
    'data': {
        'email': 'testing@example.com',
        'username': 'testing',
        'first_name': 'Tanja',
        'last_name': 'Test',
        'password1': 'testtest',
        'password2': 'testtest',
    },
}


def run_honeypot_test(db, client, testset, honeypot, exp):
    data = testset['data']
    url = reverse(testset['url'])
    if settings.HONEYPOT_ENABLED is False:
        exp = 302
        if 'contact' in url:
            exp = 200
    if honeypot is not None:
        data[sanitize_str(settings.HONEYPOT_FIELD_NAME)] = honeypot
    response = client.post(url, data)
    assert response.status_code == exp


# def test_honeypot_login(db, client):
#     run_honeypot_test(db, client, testset_login, "", 302)


# def test_honeypot_login_honeypot_field_invalid(db, client):
#     run_honeypot_test(db, client, testset_login, "some_text", 400)


# def test_honeypot_login_honeypot_field_missing(db, client):
#     run_honeypot_test(db, client, testset_login, None, 400)


def test_honeypot_signup(db, client):
    run_honeypot_test(db, client, testset_signup, settings.HONEYPOT_FIELD_VALUE, 302)


def test_honeypot_signup_honeypot_field_invalid(db, client):
    run_honeypot_test(db, client, testset_signup, 'some_text', 400)


def test_honeypot_signup_honeypot_field_missing(db, client):
    run_honeypot_test(db, client, testset_signup, None, 400)
