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
        }
    }

class RegistrationTests(TestViewMixin, MeetingsViewTestCase):

    instances = Meeting.objects.all()

    url_names = {
        'detail_view': 'meetings:registration'
    }

    def _test_registration(self, username):
        for instance in self.instances:
            msg = self.assert_detail_view(username, {
                'slug': instance.slug
            })

            if instance.registration_open:
                self.assertIn('<input type="submit" value="Register"', msg['content'])
                self.assertIn('<input type="text" name="affiliation"', msg['content'])
                self.assertIn('<input type="radio" name="dinner" value="yes"', msg['content'])
                self.assertIn('<input type="radio" name="dinner" value="no"', msg['content'])
                self.assertIn('<input type="radio" name="contribution_type" value="talk"', msg['content'])
                self.assertIn('<input type="radio" name="contribution_type" value="poster"', msg['content'])
            else:
                self.assertNotIn('<input type="submit" value="Register"', msg['content'])
                self.assertIn('The registration is currently closed.', msg['content'])


class ParticipantsTests(TestViewMixin, MeetingsViewTestCase):

    instances = Meeting.objects.all()

    url_names = {
        'detail_view': 'meetings:participants'
    }

    def _test_participants(self, username):
        for instance in self.instances:
            msg = self.assert_detail_view(username, {
                'slug': instance.slug
            })

            if instance.participants_open:
                self.assertIn('Tanja Testuser (Test)', msg['content'])
            else:
                self.assertIn('The list of participants is currently not available.', msg['content'])


class ContributionsTests(TestViewMixin, MeetingsViewTestCase):

    instances = Meeting.objects.all()

    url_names = {
        'detail_view': 'meetings:contributions'
    }

    def _test_contributions(self, username):
        for instance in self.instances:
            msg = self.assert_detail_view(username, {
                'slug': instance.slug
            })

            if instance.contributions_open:
                self.assertIn('Lorem ipsum dolor sit amet (Tanja Testuser)', msg['content'])
            else:
                self.assertIn('The list of contributions is currently not available.', msg['content'])
