from django.conf import settings
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from daiquiri.jobs.routers import JobRouter

from .views import availability, capabilities, datalink, datalink_semantics, datalink_view
from .viewsets import SyncDatalinkJobViewSet

app_name = 'datalink'

router = JobRouter(trailing_slash=False)
router.register(r'links', SyncDatalinkJobViewSet, basename='link')

urlpatterns = [
    path('', TemplateView.as_view(template_name='datalink/root.html'), name='root'),
    path('view', datalink_view, name='datalink-view'),
    path('semantics', datalink_semantics, name='datalink-semantics'),
    path('availability', availability, name='availability'),
    path('capabilities', capabilities, name='capabilities'),
]

for service in settings.DATALINK_SERVICES:
    if service['path'] != '/':
        prefix = service['path'].strip('/')
        name = prefix.replace('/', '-')
        urlpatterns.extend([
            path(
                f'{prefix}/links',
                SyncDatalinkJobViewSet.as_view(
                    {'get': 'list', 'post': 'create'}, endpoint_path=service['path']
                ),
                name=f'{name}-link-list',
            ),
            path(
                f'{prefix}/view', datalink_view,
                {'endpoint_path': service['path']}, name=f'{name}-view'
            ),
            path(
                f'{prefix}/availability', availability,
                name=f'{name}-availability'
            ),
            path(
                f'{prefix}/capabilities', capabilities,
                {'endpoint_path': service['path']}, name=f'{name}-capabilities'
            ),
        ])

urlpatterns.extend([
    path('<path:ID>/', datalink, name='datalink'),
    re_path(r'^', include(router.urls)),
])
