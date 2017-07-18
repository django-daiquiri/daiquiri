import importlib

from django.conf import settings
from django.conf.urls import url, include

from .routers import UWSRouter

router = UWSRouter(trailing_slash=False)

for resource in settings.UWS['resources']:
    module_name, class_name = resource['viewset'].rsplit('.', 1)
    viewset = getattr(importlib.import_module(module_name), class_name)
    router.register(resource['prefix'], viewset, base_name=resource['base_name'])

urlpatterns = [
    url(r'', include(router.urls)),
]
