from django.urls import include, path

from rest_framework import routers

from .views import UsersView, NewUsersView
from .viewsets import ProfileViewSet, GroupViewSet, SettingsViewSet


app_name = 'auth'

router = routers.DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'settings', SettingsViewSet, basename='settings')
router.register(r'groups', GroupViewSet)

urlpatterns = [
    # user management
    path('users/', UsersView.as_view(), name='users'),
    path('users/new/', NewUsersView.as_view(), name='users_new'),

    # rest api
    path('api/', include(router.urls)),
]
