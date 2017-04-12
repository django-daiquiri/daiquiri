from django.conf.urls import url, include

from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'databases', DatabaseViewSet, base_name='database')
router.register(r'tables', TableViewSet, base_name='table')
router.register(r'columns', ColumnViewSet, base_name='column')
router.register(r'functions', FunctionViewSet, base_name='function')
router.register(r'groups', GroupViewSet, base_name='group')
router.register(r'tabletypes', TableTypeViewSet, base_name='tabletype')


urlpatterns = [
    url(r'^db_meta/(?P<dbname>\w+)/$', dbview, name='meta_db'),
    url(r'^$', metadata, name='metadata'),

    # rest api
    url(r'^api/', include(router.urls, namespace='metadata')),
]
