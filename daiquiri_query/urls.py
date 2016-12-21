from django.conf.urls import url, include

from rest_framework import routers

from .views import query, FormViewSet, QueryJobViewSet, DatabaseViewSet, FunctionViewSet

router = routers.DefaultRouter()
router.register(r'forms', FormViewSet, base_name='form')
router.register(r'jobs', QueryJobViewSet, base_name='job')
router.register(r'databases', DatabaseViewSet, base_name='database')
router.register(r'functions', FunctionViewSet, base_name='function')

urlpatterns = [
    url(r'^$', query, name='query'),

    # rest api
    url(r'^api/', include(router.urls, namespace='query')),
]
