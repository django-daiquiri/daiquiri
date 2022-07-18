from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext, Template
from django.urls import reverse


def test_schema_menu(db, rf):
    template = "{% load metadata_tags %}{% schemas_menu %}"

    request = rf.get(reverse('home'))
    request.user = AnonymousUser()

    context = RequestContext(request, {})
    rendered_template = Template(template).render(context)

    assert 'daiquiri_data_obs' in rendered_template
