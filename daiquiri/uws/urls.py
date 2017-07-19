import importlib

from django.conf import settings
from django.conf.urls import url, include

from .routers import UWSRouter

router = UWSRouter(trailing_slash=False)

# add uws routes for the resources specified in the settings
# resources need to be of the form
# {
#    'prefix': r'query',
#    'viewset': 'daiquiri.query.viewsets.UWSQueryJobViewSet',
#    'base_name': 'uws_query'
# }
try:
    for resource in settings.UWS['resources']:
        module_name, class_name = resource['viewset'].rsplit('.', 1)
        viewset = getattr(importlib.import_module(module_name), class_name)
        router.register(resource['prefix'], viewset, base_name=resource['base_name'])
except AttributeError:
    pass

urlpatterns = [
    url(r'', include(router.urls)),
]
