from django.urls import include, path, re_path
from django.views.generic import TemplateView

from daiquiri.jobs.routers import JobRouter

from .views import availability, capabilities, datalink, datalink_semantics
from .viewsets import SyncDatalinkJobViewSet

app_name = 'datalink'

router = JobRouter(trailing_slash=False)
router.register(r'links', SyncDatalinkJobViewSet, basename='link')

urlpatterns = [
    path('', TemplateView.as_view(template_name='datalink/root.html'), name='root'),
    path('semantics', datalink_semantics, name='datalink-semantics'),
    path('<path:ID>/', datalink, name='datalink'),
    path('availability', availability, name='availability'),
    path('capabilities', capabilities, name='capabilities'),

    re_path(r'^', include(router.urls)),
]
