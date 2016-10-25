from django.conf.urls import url, include

from rest_framework import routers

from .views import contact

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', contact, name='contact'),

    # rest api
    url(r'^api/', include(router.urls, namespace='contact')),
]