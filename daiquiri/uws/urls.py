from django.conf import settings
from django.urls import include, re_path
from django.views.generic import TemplateView

from daiquiri.core.utils import import_class
from daiquiri.jobs.routers import JobRouter

app_name = 'uws'

router = JobRouter(trailing_slash=False)

'''
add uws routes for the resources specified in the settings
resources need to be of the form
{
    'prefix': r'query',
    'viewset': 'daiquiri.query.viewsets.UWSQueryJobViewSet',
    'base_name': 'uws_query'
}
'''
try:
    resources = settings.UWS_RESOURCES
except AttributeError:
    pass
else:
    for resource in resources:
        router.register(resource['prefix'], import_class(resource['viewset']), basename=resource['base_name'])

urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='uws/root.html'), name='uws_root'),
    re_path(r'', include(router.urls)),
]
