from django.urls import include, path
from rest_framework import routers

from .views import ExamplesView, JobsView, QueryView
from .viewsets import (DropdownViewSet, ExampleViewSet, FormViewSet,
                       PhaseViewSet, QueryJobViewSet, QueryLanguageViewSet,
                       QueueViewSet, StatusViewSet, DownloadViewSet)

app_name = 'query'

router = routers.DefaultRouter()
router.register(r'status', StatusViewSet, basename='status')
router.register(r'forms', FormViewSet, basename='form')
router.register(r'dropdowns', DropdownViewSet, basename='dropdown')
router.register(r'downloads', DownloadViewSet, basename='download')
router.register(r'jobs', QueryJobViewSet, basename='job')
router.register(r'examples', ExampleViewSet, basename='example')
router.register(r'queues', QueueViewSet, basename='queue')
router.register(r'querylanguages', QueryLanguageViewSet, basename='querylanguage')
router.register(r'phases', PhaseViewSet, basename='phase')

urlpatterns = [
    path(r'', QueryView.as_view(), name='query'),
    path(r'jobs/', JobsView.as_view(), name='jobs'),
    path(r'examples/', ExamplesView.as_view(), name='examples'),

    # rest api
    path(r'api/', include(router.urls)),
]
