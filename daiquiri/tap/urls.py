from django.urls import include, path, re_path
from django.views.generic import TemplateView

from daiquiri.jobs.routers import JobRouter
from daiquiri.query.viewsets import SyncQueryJobViewSet, AsyncQueryJobViewSet

from .views import availability, capabilities, tables, examples


app_name = 'tap'

router = JobRouter(trailing_slash=False)
router.register(r'sync', SyncQueryJobViewSet, base_name='sync')
router.register(r'async', AsyncQueryJobViewSet, base_name='async')

urlpatterns = [
    path('', TemplateView.as_view(template_name='tap/root.html'), name='root'),
    path('availability', availability, name='availability'),
    path('capabilities', capabilities, name='capabilities'),
    path('tables', tables, name='tables'),
    path('examples', examples, name='examples'),

    re_path(r'^', include(router.urls)),
]
