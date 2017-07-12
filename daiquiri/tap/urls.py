from django.conf.urls import url, include
from django.views.generic import TemplateView

from rest_framework import routers

from .views import sync, async, capabilities, tables, examples

# router = routers.DefaultRouter()
# router.register(r'async', UWSQueryViewSet, base_name='job')

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='tap/root.html'), name='tap_root'),
    url(r'^sync$', sync, name='tap_sync'),
    url(r'^async$', async, name='tap_async'),
    url(r'^capabilities$', capabilities, name='tap_capabilities'),
    url(r'^tables$', tables, name='tap_tables'),
    url(r'^examples$', examples, name='tap_examples'),

    # url(r'^', include(router.urls)),
]
