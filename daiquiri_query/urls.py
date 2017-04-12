from django.conf.urls import url, include

from rest_framework import routers

from .views import (
    query,
    StatusViewSet,
    FormViewSet,
    DropdownViewSet,
    QueryJobViewSet,
    ExampleViewSet,
    DatabaseViewSet,
    FunctionViewSet,
    QueueViewSet,
    QueryLanguageViewSet
)

router = routers.DefaultRouter()
router.register(r'status', StatusViewSet, base_name='status')
router.register(r'forms', FormViewSet, base_name='form')
router.register(r'dropdowns', DropdownViewSet, base_name='dropdown')
router.register(r'jobs', QueryJobViewSet, base_name='job')
router.register(r'examples', ExampleViewSet, base_name='example')
router.register(r'databases', DatabaseViewSet, base_name='database')
router.register(r'functions', FunctionViewSet, base_name='function')
router.register(r'queues', QueueViewSet, base_name='queue')
router.register(r'querylanguages', QueryLanguageViewSet, base_name='querylanguage')

urlpatterns = [
    url(r'^$', query, name='query'),

    # rest api
    url(r'^api/', include(router.urls, namespace='query')),
]
