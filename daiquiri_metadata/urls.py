from django.conf.urls import url, include

from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'databases', DatabaseViewSet)
router.register(r'tables', TableViewSet)
router.register(r'columns', ColumnViewSet)
router.register(r'functions', FunctionViewSet)

urlpatterns = [
    url(r'^$', metadata, name='metadata'),

    # rest api
    url(r'^api/', include(router.urls, namespace='metadata')),
]
