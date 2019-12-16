from django.urls import include, path
from rest_framework import routers

from .views import ArchiveView
from .viewsets import ArchiveViewSet, ColumnViewSet, FileViewSet, RowViewSet

app_name = 'archive'

router = routers.DefaultRouter()
router.register(r'rows', RowViewSet, basename='row')
router.register(r'columns', ColumnViewSet, basename='column')
router.register(r'files', FileViewSet, basename='file')
router.register(r'archives', ArchiveViewSet, basename='archive')

urlpatterns = [
    path('', ArchiveView.as_view(), name='archive'),

    # rest api
    path('api/', include(router.urls)),
]
