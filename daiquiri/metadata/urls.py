from django.urls import include, path, re_path

from rest_framework import routers

from .views import (
    ManagementView,
    SchemaView,
    TableView
)
from .viewsets import (
    SchemaViewSet,
    TableViewSet,
    ColumnViewSet,
    FunctionViewSet,
    TableTypeViewSet,
    LicenseViewSet,
    AccessLevelViewSet
)


app_name = 'metadata'

router = routers.DefaultRouter()
router.register(r'schemas', SchemaViewSet, base_name='schema')
router.register(r'tables', TableViewSet, base_name='table')
router.register(r'columns', ColumnViewSet, base_name='column')
router.register(r'functions', FunctionViewSet, base_name='function')
router.register(r'tabletypes', TableTypeViewSet, base_name='tabletype')
router.register(r'licenses', LicenseViewSet, base_name='license')
router.register(r'accesslevels', AccessLevelViewSet, base_name='accesslevel')

urlpatterns = [
    path('api/', include(router.urls)),

    path('management/', ManagementView.as_view(), name='management'),

    re_path(r'^(?P<schema_name>\w+)/$', SchemaView.as_view(), name='schema'),
    re_path(r'^(?P<schema_name>\w+)/(?P<table_name>\w+)/$', TableView.as_view(), name='table'),
]
