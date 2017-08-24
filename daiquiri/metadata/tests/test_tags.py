from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.template import RequestContext, Template


class MetadataTagsTestCase(TestCase):

    fixtures = (
        'auth.json',
        'metadata.json'
    )

    def setUp(self):
        self.request = RequestFactory().get('/')
        self.request.user = AnonymousUser()

    def test_database_menu(self):

        template = "{% load metadata_tags %}{% databases_menu %}"

        context = RequestContext(self.request, {})
        rendered_template = Template(template).render(context)

        self.assertIn('daiquiri_data_obs', rendered_template)
