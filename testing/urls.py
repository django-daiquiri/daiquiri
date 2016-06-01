from django.conf.urls import include, url
from django.contrib import admin

from daiquiri_core.views import home

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^auth/', include('daiquiri_auth.urls_auth')),
    url(r'^accounts/', include('daiquiri_auth.urls_accounts')),
    url(r'^uws/', include('daiquiri_jobs.urls', namespace='uws')),
    url(r'^admin/', include(admin.site.urls)),
]
