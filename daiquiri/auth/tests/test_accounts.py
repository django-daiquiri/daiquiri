from django.core.urlresolvers import reverse
from django.test import TestCase

from ..models import Profile


class AccountsTestCase(TestCase):

    fixtures = (
        'auth.json',
    )

    def test_login(self):
        url = reverse('account_login')
        response = self.client.post(url, {
            'login': 'user',
            'password': 'user'
        })
        self.assertRedirects(response, reverse('home'))

    def test_invalid(self):
        url = reverse('account_login')
        response = self.client.post(url, {
            'login': 'invalid',
            'password': 'invalid'
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        url = reverse('account_logout')
        response = self.client.post(url)
        self.assertRedirects(response, reverse('home'))

    def test_signup_get(self):
        url = reverse('account_signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_signup_post(self):
        url = reverse('account_signup')
        response = self.client.post(url, {
            'email': 'test@example.com',
            'username': 'test',
            'first_name': 'Tanja',
            'last_name': 'Test',
            'password1': 'testing',
            'password2': 'testing'
        })

        # check that the signup redirects to the pending page or the confirm email page
        self.assertEqual(response.status_code, 302)

        # check that a profile was created
        profile = Profile.objects.get(user__username='test')
        self.assertEqual(profile.is_pending, True)

    def test_signup_post_invalid(self):
        url = reverse('account_signup')
        response = self.client.post(url, {
            'email': 'test@example.com',
            'username': 'test',
            'first_name': 'Tanja',
            'last_name': 'Test',
            'password1': 'testing',
            'password2': 'invalid'
        })

        # check that the signup returns 200 (with validation error)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '* You must type the same password each time.')

        # check that a profile was not created
        exists = Profile.objects.filter(user__username='test').exists()
        self.assertEqual(exists, False)

    def test_signup_post_exists(self):
        url = reverse('account_signup')
        response = self.client.post(url, {
            'email': 'user@example.com',
            'username': 'user',
            'first_name': 'Tanja',
            'last_name': 'Test',
            'password1': 'testing',
            'password2': 'testing'
        })

        # check that the signup returns 200 (with validation error)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '* A user with that username already exists.')
        self.assertContains(response, '* A user is already registered with this e-mail address.')

        # check that a profile was not created
        exists = Profile.objects.filter(user__username='test').exists()
        self.assertEqual(exists, False)

    def test_profile_get_for_user(self):
        self.client.login(username='user', password='user')

        url = reverse('account_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_get_for_anonymous(self):
        url = reverse('account_profile')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('account_login') + '?next=' + url)

    def test_profile_post_for_user(self):
        self.client.login(username='user', password='user')

        url = reverse('account_profile')
        response = self.client.post(url, {
            'first_name': 'Tanja',
            'last_name': 'Test',
        })
        self.assertRedirects(response, reverse('home'))

    def test_profile_cancel_for_user(self):
        self.client.login(username='user', password='user')

        url = reverse('account_profile')
        response = self.client.post(url, {
            'cancel': True
        })
        self.assertRedirects(response, reverse('home'))

    def test_profile_post_for_anonymous(self):
        url = reverse('account_profile')
        response = self.client.post(url, {
            'first_name': 'Tanja',
            'last_name': 'Test',
        })
        self.assertRedirects(response, reverse('account_login') + '?next=' + url)

    def test_profile_json_get_for_user(self):
        self.client.login(username='user', password='user')

        url = reverse('account_profile_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_json_get_for_anonymous(self):
        url = reverse('account_profile_json')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('account_login') + '?next=' + url)

    def test_token_get_for_user(self):
        self.client.login(username='user', password='user')

        url = reverse('account_token')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_token_get_for_anonymous(self):
        url = reverse('account_token')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('account_login') + '?next=' + url)

    def test_token_post_for_user(self):
        self.client.login(username='user', password='user')

        url = reverse('account_token')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_token_post_for_anonymous(self):
        url = reverse('account_token')
        response = self.client.post(url)
        self.assertRedirects(response, reverse('account_login') + '?next=' + url)
