from django.conf.urls import url, include
from django.views.generic import TemplateView

from daiquiri.jobs.routers import JobRouter
from daiquiri.query.viewsets import SyncQueryJobViewSet, AsyncQueryJobViewSet

from .views import availability, capabilities, tables, examples


router = JobRouter(trailing_slash=False)
router.register(r'sync', SyncQueryJobViewSet, base_name='sync')
router.register(r'async', AsyncQueryJobViewSet, base_name='async')

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='tap/root.html'), name='root'),
    url(r'^availability$', availability, name='availability'),
    url(r'^capabilities$', capabilities, name='capabilities'),
    url(r'^tables$', tables, name='tables'),
    url(r'^examples$', examples, name='examples'),

    url(r'^', include(router.urls)),
]
