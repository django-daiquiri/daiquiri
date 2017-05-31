from django.conf.urls import url, include
from django.views.generic import TemplateView

from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    url(r'^profile/$', profile_update, name='account_profile'),
    url(r'^pending/$', TemplateView.as_view(template_name='account/account_pending.html'), name='account_pending'),
    url(r'^', include('allauth.urls')),
]
