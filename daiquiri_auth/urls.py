from django.conf.urls import url

urlpatterns = [
    url(r'^update-profile/$', 'daiquiri_auth.views.profile_update', name='profile_update'),
]
