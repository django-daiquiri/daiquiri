from django.conf.urls import url, include

from rest_framework import routers

from .views import QueryView, ExamplesView
from .viewsets import (
    StatusViewSet,
    FormViewSet,
    DropdownViewSet,
    QueryJobViewSet,
    ExampleViewSet,
    QueueViewSet,
    QueryLanguageViewSet
)

router = routers.DefaultRouter()
router.register(r'status', StatusViewSet, base_name='status')
router.register(r'forms', FormViewSet, base_name='form')
router.register(r'dropdowns', DropdownViewSet, base_name='dropdown')
router.register(r'jobs', QueryJobViewSet, base_name='job')
router.register(r'examples', ExampleViewSet, base_name='example')
router.register(r'queues', QueueViewSet, base_name='queue')
router.register(r'querylanguages', QueryLanguageViewSet, base_name='querylanguage')

urlpatterns = [
    url(r'^$', QueryView.as_view(), name='query'),
    url(r'^examples/', ExamplesView.as_view(), name='examples'),

    # rest api
    url(r'^api/', include(router.urls)),
]
