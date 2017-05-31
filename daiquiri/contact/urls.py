from django.conf.urls import url, include

from rest_framework import routers

from .views import (
    contact,
    messages,
    ContactMessageViewSet,
    StatusViewSet
)

router = routers.DefaultRouter()
router.register(r'messages', ContactMessageViewSet, base_name='message')
router.register(r'status', StatusViewSet, base_name='status')

urlpatterns = [
    url(r'^$', contact, name='contact'),
    url(r'^messages/', messages, name='messages'),

    # rest api
    url(r'^api/', include(router.urls, namespace='contact')),
]
