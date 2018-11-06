from django.urls import include, path

from rest_framework import routers

from .views import contact, MessagesView
from .viewsets import ContactMessageViewSet, StatusViewSet


app_name = 'contact'

router = routers.DefaultRouter()
router.register(r'messages', ContactMessageViewSet, base_name='message')
router.register(r'status', StatusViewSet, base_name='status')

urlpatterns = [
    path('', contact, name='contact'),
    path('messages/', MessagesView.as_view(), name='messages'),

    # rest api
    path('api/', include(router.urls)),
]
