from daiquiri.jobs.routers import JobRouter
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from .views import availability, capabilities, datalink
from .viewsets import SyncDatalinkJobViewSet

app_name = 'datalink'

router = JobRouter(trailing_slash=False)
router.register(r'links', SyncDatalinkJobViewSet, basename='link')

urlpatterns = [
    path('', TemplateView.as_view(template_name='datalink/root.html'), name='root'),
    path('<str:ID>/', datalink, name='datalink'),
    path('availability', availability, name='availability'),
    path('capabilities', capabilities, name='capabilities'),

    re_path(r'^', include(router.urls)),
]
