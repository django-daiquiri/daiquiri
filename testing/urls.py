from django.conf import settings

from django.conf.urls import include, url
from django.contrib import admin

from daiquiri_core.views import home
from daiquiri_auth.views import login, logout


urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^auth/', include('daiquiri_auth.urls')),
    url(r'^uws/', include('daiquiri_jobs.urls', namespace='uws')),
    url(r'^%s/' % settings.LOGIN_URL.strip('/'), login, name='login'),
    url(r'^%s/' % settings.LOGOUT_URL.strip('/'), logout, name='logout'),
    url(r'^admin/', include(admin.site.urls)),
]
