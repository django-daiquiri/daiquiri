from django.urls import reverse

from ..models import Profile


def test_login(db, client):
    url = reverse('account_login')
    response = client.post(url, {
        'login': 'user',
        'password': 'user'
    })
    assert response.status_code == 302
    assert response.url == reverse('home')


def test_invalid(db, client):
    url = reverse('account_login')
    response = client.post(url, {
        'login': 'invalid',
        'password': 'invalid'
    })
    assert response.status_code == 200


def test_logout(db, client):
    url = reverse('account_logout')
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('home')


def test_signup_get(db, client):
    url = reverse('account_signup')
    response = client.get(url)
    assert response.status_code == 200


def test_signup_post(db, client):
    url = reverse('account_signup')
    response = client.post(url, {
        'email': 'testing@example.com',
        'username': 'testing',
        'first_name': 'Tanja',
        'last_name': 'Test',
        'password1': 'testing',
        'password2': 'testing'
    })

    # check that the signup redirects to the pending page or the confirm email page
    assert response.status_code == 302

    # check that a profile was created
    profile = Profile.objects.get(user__username='testing')
    assert profile.is_pending is True


def test_signup_post_invalid(db, client):
    url = reverse('account_signup')
    response = client.post(url, {
        'email': 'testing@example.com',
        'username': 'testing',
        'first_name': 'Tanja',
        'last_name': 'Test',
        'password1': 'testing',
        'password2': 'invalid'
    })

    # check that the signup returns 200 (with validation error)
    assert response.status_code == 200
    assert b'* You must type the same password each time.' in response.content

    # check that a profile was not created
    assert Profile.objects.filter(user__username='testing').exists() is False


def test_signup_post_exists(db, client):
    url = reverse('account_signup')
    response = client.post(url, {
        'email': 'user@example.com',
        'username': 'user',
        'first_name': 'Tanja',
        'last_name': 'Test',
        'password1': 'testing',
        'password2': 'testing'
    })

    # check that the signup returns 200 (with validation error)
    assert response.status_code == 200
    assert b'* A user with that username already exists.' in response.content
    assert b'* A user is already registered with this e-mail address.' in response.content

    # check that a profile was not created
    assert Profile.objects.filter(user__username='testing').exists() is False


def test_profile_get_for_user(db, client):
    client.login(username='user', password='user')

    url = reverse('account_profile')
    response = client.get(url)
    assert response.status_code == 200


def test_profile_get_for_anonymous(db, client):
    url = reverse('account_profile')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('account_login') + '?next=' + url


def test_profile_post_for_user(db, client):
    client.login(username='user', password='user')

    url = reverse('account_profile')
    response = client.post(url, {
        'first_name': 'Tanja',
        'last_name': 'Test',
    })
    assert response.status_code == 302
    assert response.url == reverse('home')


def test_profile_cancel_for_user(db, client):
    client.login(username='user', password='user')

    url = reverse('account_profile')
    response = client.post(url, {
        'cancel': True
    })
    assert response.status_code == 302
    assert response.url == reverse('home')


def test_profile_post_for_anonymous(db, client):
    url = reverse('account_profile')
    response = client.post(url, {
        'first_name': 'Tanja',
        'last_name': 'Test',
    })
    assert response.status_code == 302
    assert response.url == reverse('account_login') + '?next=' + url


def test_profile_json_get_for_user(db, client):
    client.login(username='user', password='user')

    url = reverse('account_profile_json')
    response = client.get(url)
    assert response.status_code == 200


def test_profile_json_get_for_anonymous(db, client):
    url = reverse('account_profile_json')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('account_login') + '?next=' + url


def test_token_get_for_user(db, client):
    client.login(username='user', password='user')

    url = reverse('account_token')
    response = client.get(url)
    assert response.status_code == 200


def test_token_get_for_anonymous(db, client):
    url = reverse('account_token')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('account_login') + '?next=' + url


def test_token_post_for_user(db, client):
    client.login(username='user', password='user')

    url = reverse('account_token')
    response = client.post(url)
    assert response.status_code == 200


def test_token_post_for_anonymous(db, client):
    url = reverse('account_token')
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('account_login') + '?next=' + url
