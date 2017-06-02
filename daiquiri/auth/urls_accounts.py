from django.conf.urls import url, include
from django.views.generic import TemplateView

from .views import profile_update


urlpatterns = [
    url(r'^profile/$', profile_update, name='account_profile'),
    url(r'^pending/$', TemplateView.as_view(template_name='account/account_pending.html'), name='account_pending'),
    url(r'^', include('allauth.urls')),
]
