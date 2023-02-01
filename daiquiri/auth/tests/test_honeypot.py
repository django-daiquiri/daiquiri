from django.conf import settings
from django.urls import reverse

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
        "password2": "testing",
    },
}

testset_contact = {
    "url": "contact:contact",
    "data": {"subject": "Test", "message": "This is a test."},
}


def run_honeypot_test(db, client, testset, honeypot, exp):
    data = testset["data"]
    url = reverse(testset["url"])
    if honeypot is not None:
        data[settings.HONEYPOT_FIELD_NAME] = honeypot
    response = client.post(url, data)
    assert response.status_code == exp


# def test_honeypot_login(db, client):
#     run_honeypot_test(db, client, testset_login, "", 302)


# def test_honeypot_login_honeypot_field_invalid(db, client):
#     run_honeypot_test(db, client, testset_login, "some_text", 400)


# def test_honeypot_login_honeypot_field_missing(db, client):
#     run_honeypot_test(db, client, testset_login, None, 400)


# def test_honeypot_signup(db, client):
#     run_honeypot_test(db, client, testset_signup, "", 302)


# def test_honeypot_signup_honeypot_field_invalid(db, client):
#     run_honeypot_test(db, client, testset_signup, "some_text", 400)


# def test_honeypot_signup_honeypot_field_missing(db, client):
#     run_honeypot_test(db, client, testset_signup, None, 400)


def test_contact_post(db, client):
    client.login(username="admin", password="admin")
    run_honeypot_test(db, client, testset_contact, "", 200)


def test_contact_post_honeypot_field_invalid(db, client):
    client.login(username="admin", password="admin")
    run_honeypot_test(db, client, testset_contact, "some_text", 400)


def test_contact_post_honeypot_field_missing(db, client):
    client.login(username="admin", password="admin")
    run_honeypot_test(db, client, testset_contact, None, 400)
