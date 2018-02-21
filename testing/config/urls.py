from django.conf.urls import include, url
from django.contrib import admin

from daiquiri.core.views import home

urlpatterns = [
    url(r'^$', home, name='home'),

    url(r'^accounts/', include('daiquiri.auth.urls_accounts')),

    url(r'^archive/', include('daiquiri.archive.urls', namespace='archive')),
    url(r'^auth/', include('daiquiri.auth.urls_auth', namespace='auth')),
    url(r'^contact/', include('daiquiri.contact.urls', namespace='contact')),
    url(r'^files/', include('daiquiri.files.urls', namespace='files')),
    url(r'^metadata/', include('daiquiri.metadata.urls', namespace='metadata')),
    url(r'^serve/', include('daiquiri.serve.urls', namespace='serve')),
    url(r'^query/', include('daiquiri.query.urls', namespace='query')),
    url(r'^tap/', include('daiquiri.tap.urls', namespace='tap')),
    url(r'^uws/', include('daiquiri.uws.urls', namespace='uws')),

    url(r'^admin/', include(admin.site.urls)),
]

handler400 = 'daiquiri.core.views.bad_request'
handler403 = 'daiquiri.core.views.forbidden'
handler404 = 'daiquiri.core.views.not_found'
handler500 = 'daiquiri.core.views.internal_server_error'
