from django.test import TestCase

from test_generator.views import TestViewMixin

from ..models import Meeting


class MeetingsViewTestCase(TestCase):

    fixtures = (
        'auth.json',
        'meetings.json'
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('anonymous', None),
    )

    status_map = {
        'detail_view': {
            'admin': 200, 'user': 200, 'anonymous': 200
        },
        'detail_view_not_found': {
            'admin': 404, 'user': 404, 'anonymous': 404
        },
        'update_view_get': {
            'admin': 200, 'user': 200, 'anonymous': 200
        },
        'update_view_post': {
            'admin': 302, 'user': 302, 'anonymous': 302
        }
    }

class RegistrationTests(TestViewMixin, MeetingsViewTestCase):

    url_names = {
        'update_view': 'meetings:registration'
    }

    def _test_open_get(self, username):
        instance = Meeting.objects.filter(registration_open=True).first()

        msg = self.assert_update_view_get(username, {
            'slug': instance.slug
        })

        self.assertIn(b'<input type="submit" value="Register"', msg['content'])
        self.assertIn(b'<input type="text" name="affiliation"', msg['content'])
        self.assertIn(b'<input type="radio" name="dinner" value="yes"', msg['content'])
        self.assertIn(b'<input type="radio" name="dinner" value="no"', msg['content'])
        self.assertIn(b'<input type="radio" name="contribution_type" value="talk"', msg['content'])
        self.assertIn(b'<input type="radio" name="contribution_type" value="poster"', msg['content'])

    def _test_open_post(self, username):
        instance = Meeting.objects.filter(registration_open=True).first()

        self.assert_update_view_post(username, {
            'slug': instance.slug
        }, {
            'first_name': 'Thomas',
            'last_name': 'Test',
            'email': username + '@example.com',
            'affiliation': 'Test',
            'dinner': 'no',
            'contribution_type': 'talk',
            'title': 'Lorem ipsum dolor sit amet',
            'abstract': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est. Lorem ipsum dolor sit amet.'
        })

    def _test_open_post_no_contribution(self, username):
        instance = Meeting.objects.filter(registration_open=True).first()

        self.assert_update_view_post(username, {
            'slug': instance.slug
        }, {
            'first_name': 'Thomas',
            'last_name': 'Test',
            'email': username + '@example.com',
            'affiliation': 'Test',
            'dinner': 'no'
        })

    def _test_closed_get(self, username):
        instance = Meeting.objects.filter(registration_open=False).first()

        msg = self.assert_update_view_get(username, {
            'slug': instance.slug
        })

        self.assertNotIn(b'<input type="submit" value="Register"', msg['content'])
        self.assertIn(b'The registration is currently closed.', msg['content'])

    def _test_not_found_get(self, username):
        self.assert_view('detail_view_not_found', 'get', 'update_view', username, {
            'slug': 'invalid'
        })


class RegistrationDoneTests(TestViewMixin, MeetingsViewTestCase):

    url_names = {
        'detail_view': 'meetings:registration_done'
    }

    def _test_open(self, username):
        instance = Meeting.objects.filter(registration_open=True).first()

        msg = self.assert_detail_view(username, {
            'slug': instance.slug
        })

        self.assertNotIn(b'The registration is currently closed.', msg['content'])

    def _test_closed(self, username):
        instance = Meeting.objects.filter(registration_open=False).first()

        msg = self.assert_detail_view(username, {
            'slug': instance.slug
        })

        self.assertIn(b'The registration is currently closed.', msg['content'])

    def _test_not_found(self, username):
        self.assert_view('detail_view_not_found', 'get', 'detail_view', username, {
            'slug': 'invalid'
        })

class ParticipantsTests(TestViewMixin, MeetingsViewTestCase):

    url_names = {
        'detail_view': 'meetings:participants'
    }

    def _test_open(self, username):
        instance = Meeting.objects.filter(participants_open=True).first()

        msg = self.assert_detail_view(username, {
            'slug': instance.slug
        })

        self.assertIn(b'Tanja Testuser (Test)', msg['content'])

    def _test_closed(self, username):
        instance = Meeting.objects.filter(participants_open=False).first()

        msg = self.assert_detail_view(username, {
            'slug': instance.slug
        })

        self.assertIn(b'The list of participants is currently not available.', msg['content'])

    def _test_not_found(self, username):
        self.assert_view('detail_view_not_found', 'get', 'detail_view', username, {
            'slug': 'invalid'
        })

class ContributionsTests(TestViewMixin, MeetingsViewTestCase):

    url_names = {
        'detail_view': 'meetings:contributions'
    }

    def _test_open(self, username):
        instance = Meeting.objects.filter(contributions_open=True).first()

        msg = self.assert_detail_view(username, {
            'slug': instance.slug
        })

        self.assertIn(b'Lorem ipsum dolor sit amet (Tanja Testuser)', msg['content'])

    def _test_closed(self, username):
        instance = Meeting.objects.filter(contributions_open=False).first()

        msg = self.assert_detail_view(username, {
            'slug': instance.slug
        })

        self.assertIn(b'The list of contributions is currently not available.', msg['content'])

    def _test_not_found(self, username):
        self.assert_view('detail_view_not_found', 'get', 'detail_view', username, {
            'slug': 'invalid'
        })
