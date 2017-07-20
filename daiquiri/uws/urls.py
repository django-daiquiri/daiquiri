import importlib

from django.conf import settings
from django.conf.urls import url, include
from django.views.generic import TemplateView

from daiquiri.dali.routers import JobRouter


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
    resources = settings.UWS['resources']
except AttributeError:
    pass
else:
    for resource in resources:
        module_name, class_name = resource['viewset'].rsplit('.', 1)
        viewset = getattr(importlib.import_module(module_name), class_name)
        router.register(resource['prefix'], viewset, base_name=resource['base_name'])

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='uws/root.html'), name='uws_root'),
    url(r'', include(router.urls)),
]
