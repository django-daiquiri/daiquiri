from django.conf import settings
from django.urls import reverse

from ..models import Profile


def test_honeypot_login(db, client):
    settings.MIDDLEWARE.append('honeypot.middleware.HoneypotMiddleware')
    url = reverse('account_login')
    response = client.post(url, {
        'login': 'user',
        'password': 'user',
        settings.HONEYPOT_FIELD_NAME: "",
    })
    settings.MIDDLEWARE.remove('honeypot.middleware.HoneypotMiddleware')
    assert response.status_code == 302
    assert response.url == reverse('home')

def test_honeypot_signup_post(db, client):
    settings.MIDDLEWARE.append('honeypot.middleware.HoneypotMiddleware')
    url = reverse('account_signup')
    response = client.post(url, {
        'email': 'testing@example.com',
        'username': 'testing',
        'first_name': 'Tanja',
        'last_name': 'Test',
        'password1': 'testing',
        'password2': 'testing',
        settings.HONEYPOT_FIELD_NAME: "",
    })
    settings.MIDDLEWARE.remove('honeypot.middleware.HoneypotMiddleware')
    # check that the signup redirects to the pending page or the confirm email page
    assert response.status_code == 302

    # check that a profile was created
    profile = Profile.objects.get(user__username='testing')
    assert profile.is_pending is True

def test_honeypot_login_field_not_empty(db, client):
    settings.MIDDLEWARE.append('honeypot.middleware.HoneypotMiddleware')
    url = reverse('account_login')
    response = client.post(url, {
        'login': 'user',
        'password': 'user',
        settings.HONEYPOT_FIELD_NAME: "some text here",
    })
    settings.MIDDLEWARE.remove('honeypot.middleware.HoneypotMiddleware')
    assert response.status_code == 400

def test_honeypot_login_field_missing(db, client):
    settings.MIDDLEWARE.append('honeypot.middleware.HoneypotMiddleware')
    url = reverse('account_login')
    response = client.post(url, {
        'login': 'user',
        'password': 'user',
    })
    settings.MIDDLEWARE.remove('honeypot.middleware.HoneypotMiddleware')
    assert response.status_code == 400
