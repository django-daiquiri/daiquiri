from django.contrib import admin
from django.urls import include, path

from daiquiri.core.views import home

urlpatterns = [
    path('', home, name='home'),

    path('accounts/', include('daiquiri.auth.urls_accounts')),

    path('auth/', include('daiquiri.auth.urls_auth', namespace='auth')),
    path('conesearch/', include('daiquiri.conesearch.urls', namespace='conesearch')),
    path('contact/', include('daiquiri.contact.urls', namespace='contact')),
    path('datalink/', include('daiquiri.datalink.urls', namespace='datalink')),
    path('files/', include('daiquiri.files.urls', namespace='files')),
    path('metadata/', include('daiquiri.metadata.urls', namespace='metadata')),
    path('oai/', include('daiquiri.oai.urls', namespace='oai')),
    path('serve/', include('daiquiri.serve.urls', namespace='serve')),
    path('stats/', include('daiquiri.stats.urls', namespace='stats')),
    path('query/', include('daiquiri.query.urls', namespace='query')),
    path('tap/', include('daiquiri.tap.urls', namespace='tap')),
    path('uws/', include('daiquiri.uws.urls', namespace='uws')),

    path('admin/', admin.site.urls),
]

handler400 = 'daiquiri.core.views.bad_request'
handler403 = 'daiquiri.core.views.forbidden'
handler404 = 'daiquiri.core.views.not_found'
handler500 = 'daiquiri.core.views.internal_server_error'
