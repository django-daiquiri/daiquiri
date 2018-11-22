from django.urls import include, path

from rest_framework import routers

from .views import UsersView
from .viewsets import ProfileViewSet, GroupViewSet


app_name = 'auth'

router = routers.DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    # user management
    path('users/', UsersView.as_view(), name='users'),

    # rest api
    path('api/', include(router.urls)),
]
