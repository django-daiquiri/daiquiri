from django.conf.urls import url, include

from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register(r'messages', ContactMessageViewSet)

urlpatterns = [
    url(r'^messages/', messages, name='messages'),
    url(r'^$', contact, name='contact'),


    # rest api
    url(r'^api/', include(router.urls, namespace='contact')),
]
