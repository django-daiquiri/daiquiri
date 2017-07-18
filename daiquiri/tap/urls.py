from django.conf.urls import url, include
from django.views.generic import TemplateView

from daiquiri.uws.routers import UWSRouter
from daiquiri.uws.viewsets import QueryJobViewSet

from .views import sync, capabilities, tables, examples

router = UWSRouter()
router.register(r'async', QueryJobViewSet, base_name='tapquery')

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='tap/root.html'), name='tap_root'),
    url(r'^sync$', sync, name='tap_sync'),
    url(r'^capabilities$', capabilities, name='tap_capabilities'),
    url(r'^tables$', tables, name='tap_tables'),
    url(r'^examples$', examples, name='tap_examples'),

    url(r'^', include(router.urls)),
]
