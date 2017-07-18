from django.conf.urls import url, include
from django.views.generic import TemplateView

from daiquiri.uws.routers import UWSRouter

from .views import capabilities, tables, examples
from .viewsets import SyncQueryJobViewSet, AsyncQueryJobViewSet

router = UWSRouter()
router.register(r'sync', SyncQueryJobViewSet, base_name='tap_sync')
router.register(r'async', AsyncQueryJobViewSet, base_name='tap_async')

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='tap/root.html'), name='tap_root'),
    url(r'^capabilities$', capabilities, name='tap_capabilities'),
    url(r'^tables$', tables, name='tap_tables'),
    url(r'^examples$', examples, name='tap_examples'),

    url(r'^', include(router.urls)),
]
