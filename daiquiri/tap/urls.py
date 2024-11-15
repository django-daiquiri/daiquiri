from django.urls import include, path, re_path
from django.views.generic import TemplateView

from daiquiri.jobs.routers import JobRouter
from daiquiri.query.viewsets import AsyncQueryJobViewSet, SyncQueryJobViewSet

from .views import availability, capabilities, examples, resource, tables

app_name = 'tap'

router = JobRouter(trailing_slash=False)
router.register(r'sync', SyncQueryJobViewSet, basename='sync')
router.register(r'async', AsyncQueryJobViewSet, basename='async')

urlpatterns = [
    path('', TemplateView.as_view(template_name='tap/root.html'), name='root'),
    path('resource', resource, name='resource'),
    path('availability', availability, name='availability'),
    path('capabilities', capabilities, name='capabilities'),
    path('tables', tables, name='tables'),
    path('examples', examples, name='examples'),

    re_path(r'^', include(router.urls)),
]
