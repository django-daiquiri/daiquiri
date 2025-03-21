from django.urls import include, re_path
from django.views.generic import TemplateView

from .views import logout, password_change, password_set, profile_json, profile_update, terms_of_use, token

urlpatterns = [
    re_path(r'^profile/$', profile_update, name='account_profile'),
    re_path(r'^profile.json/$', profile_json, name='account_profile_json'),
    re_path(r'^token/$', token, name='account_token'),
    re_path(r'^pending/$', TemplateView.as_view(template_name='account/account_pending.html'), name='account_pending'),

    re_path(r"^logout/$", logout, name="account_logout"),

    # include allauth patterns
    re_path(r'^password/change/$', password_change, name='account_change_password'),
    re_path(r'^password/change/done/$', TemplateView.as_view(template_name='account/password_change_done.html'), name='account_change_password_done'),  # noqa: E501
    re_path(r'^password/set/$', password_set, name='account_password_set'),
    re_path(r'^password/set/done/$', TemplateView.as_view(template_name='account/password_set_done.html'), name='account_set_password_done'),  # noqa: E501
    re_path(r'^terms_of_use/$', terms_of_use, name='terms_of_use'),
    re_path(r'^', include('allauth.urls')),
]
