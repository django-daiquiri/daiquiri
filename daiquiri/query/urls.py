from django.urls import include, path, re_path

from rest_framework import routers

from .views import QueryView
from .viewsets import (
    DownloadViewSet,
    DropdownViewSet,
    ExampleViewSet,
    FormViewSet,
    PhaseViewSet,
    QueryDownloadFormatViewSet,
    QueryJobViewSet,
    QueryLanguageViewSet,
    QueueViewSet,
    StatusViewSet,
)

app_name = 'query'

router = routers.DefaultRouter()
router.register(r'status', StatusViewSet, basename='status')
router.register(r'forms', FormViewSet, basename='form')
router.register(r'dropdowns', DropdownViewSet, basename='dropdown')
router.register(r'downloads', DownloadViewSet, basename='download')
router.register(r'downloadformats', QueryDownloadFormatViewSet, basename='downloadformat')
router.register(r'jobs', QueryJobViewSet, basename='job')
router.register(r'examples', ExampleViewSet, basename='example')
router.register(r'queues', QueueViewSet, basename='queue')
router.register(r'querylanguages', QueryLanguageViewSet, basename='querylanguage')
router.register(r'phases', PhaseViewSet, basename='phase')

urlpatterns = [
    # rest api
    path(r'api/', include(router.urls)),

    # query interface, needs to be last in list
    # the default path is required to cover a case with a single trailing slash
    re_path(r'^$', QueryView.as_view(), name='default'),
    re_path(r'[A-Za-z0-9-]*/$', QueryView.as_view(), name='query'),
]
