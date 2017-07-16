from django.conf.urls import url, include
from django.views.generic import TemplateView

from daiquiri.uws.routers import UWSRouter

from .views import sync, capabilities, tables, examples
from .viewsets import QueryJobsViewSet

router = UWSRouter()
router.register(r'async', QueryJobsViewSet, base_name='tapquery')

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='tap/root.html'), name='tap_root'),
    url(r'^sync$', sync, name='tap_sync'),
    url(r'^capabilities$', capabilities, name='tap_capabilities'),
    url(r'^tables$', tables, name='tap_tables'),
    url(r'^examples$', examples, name='tap_examples'),

    url(r'^', include(router.urls)),
]
