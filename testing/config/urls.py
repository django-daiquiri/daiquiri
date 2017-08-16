from django.conf.urls import include, url
from django.contrib import admin
from django.views.i18n import javascript_catalog

from daiquiri.core.views import home

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^auth/', include('daiquiri.auth.urls_auth')),
    url(r'^accounts/', include('daiquiri.auth.urls_accounts')),
    url(r'^metadata/', include('daiquiri.metadata.urls')),
    url(r'^serve/', include('daiquiri.serve.urls')),
    url(r'^query/', include('daiquiri.query.urls')),
    url(r'^contact/', include('daiquiri.contact.urls')),
    url(r'^uws/', include('daiquiri.uws.urls')),
    url(r'^tap/', include('daiquiri.tap.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^jsi18n/$', javascript_catalog, name='javascript-catalog'),
]
