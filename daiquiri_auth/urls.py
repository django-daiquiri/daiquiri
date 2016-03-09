from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from rest_framework import routers

from .views import profile_update, UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^update-profile/$', profile_update, name='profile_update'),

    # change password
    url(r'^password/change/$', auth_views.password_change, {
        'template_name': 'auth/password_change_form.html'
        }, name='password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done, {
        'template_name': 'auth/password_change_done.html'
        }, name='password_change_done'),

    # reset password
    url(r'^password/reset/$', auth_views.password_reset, {
        'template_name': 'auth/password_reset_form.html',
        'email_template_name': 'auth/password_reset_email.txt',
        'subject_template_name': 'auth/password_reset_subject.txt',
        }, name='password_reset'),
    url(r'^password/reset/done/$', auth_views.password_reset_done, {
        'template_name': 'auth/password_reset_done.html',
        }, name='password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, {
        'template_name': 'auth/password_reset_confirm.html',
        }, name='password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete, {
        'template_name': 'auth/password_reset_complete.html',
        }, name='password_reset_complete'),

    url(r'^api/', include(router.urls)),
]