from django.conf.urls import url, include
from django.views.generic import TemplateView

from .views import profile_update, profile_json, token, logout


urlpatterns = [
    url(r'^profile/$', profile_update, name='account_profile'),
    url(r'^profile.json/$', profile_json, name='account_profile_json'),
    url(r'^token/$', token, name='account_token'),
    url(r'^pending/$', TemplateView.as_view(template_name='account/account_pending.html'), name='account_pending'),

    # override login by allauth to remove wordpress cookies
    url(r"^logout/$", logout, name="account_logout"),

    # include allauth patterns
    url(r'^', include('allauth.urls')),
]
