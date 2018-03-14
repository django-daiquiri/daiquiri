from django.conf.urls import url, include
from django.views.generic import TemplateView

from .views import profile_update, profile_json, token, logout, password_change, password_set


urlpatterns = [
    url(r'^profile/$', profile_update, name='account_profile'),
    url(r'^profile.json/$', profile_json, name='account_profile_json'),
    url(r'^token/$', token, name='account_token'),
    url(r'^pending/$', TemplateView.as_view(template_name='account/account_pending.html'), name='account_pending'),

    # override login by allauth to remove wordpress cookies
    url(r"^logout/$", logout, name="account_logout"),

    # include allauth patterns
    url(r'^password/change/$', password_change, name='account_change_password'),
    url(r'^password/change/done/$', TemplateView.as_view(template_name='account/password_change_done.html'), name='account_change_password_done'),
    url(r'^password/set/$', password_set, name='account_password_set'),
    url(r'^', include('allauth.urls')),
]
