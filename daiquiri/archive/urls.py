from django.urls import include, path

from rest_framework import routers

from .views import ArchiveView
from .viewsets import RowViewSet, ColumnViewSet, FileViewSet, ArchiveViewSet

app_name = 'archive'

router = routers.DefaultRouter()
router.register(r'rows', RowViewSet, base_name='row')
router.register(r'columns', ColumnViewSet, base_name='column')
router.register(r'files', FileViewSet, base_name='file')
router.register(r'archives', ArchiveViewSet, base_name='archive')

urlpatterns = [
    path('', ArchiveView.as_view(), name='archive'),

    # rest api
    path('api/', include(router.urls)),
]
