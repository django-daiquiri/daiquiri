from django.conf.urls import url, include

from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    url(r'^profile/', profile_update, name='account_profile'),
    url(r'^', include('allauth.urls')),
]
