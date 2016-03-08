from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^update-profile/$', 'daiquiri_auth.views.profile_update', name='profile_update'),

    # change password
    url(r'^password/change/$', auth_views.password_change, {
        'template_name': 'auth/password_change_form.html'
        }, name='password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done, {
        'template_name': 'auth/password_change_done.html'
        }, name='password_change_done'),
]
