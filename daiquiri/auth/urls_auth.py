from django.conf.urls import url, include

from rest_framework import routers

from .views import UsersView
from .viewsets import ProfileViewSet, GroupViewSet

router = routers.DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    # user management
    url(r'^users/', UsersView.as_view(), name='users'),

    # rest api
    url(r'^api/', include(router.urls)),
]
