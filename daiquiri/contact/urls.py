from django.urls import include, path

from rest_framework import routers

from .views import MessagesView, contact
from .viewsets import ContactMessageViewSet, StatusViewSet

app_name = 'contact'

router = routers.DefaultRouter()
router.register(r'messages', ContactMessageViewSet, basename='message')
router.register(r'status', StatusViewSet, basename='status')

urlpatterns = [
    path('', contact, name='contact'),
    path('messages/', MessagesView.as_view(), name='messages'),

    # rest api
    path('api/', include(router.urls)),
]
