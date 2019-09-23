from daiquiri.core.routers import DaiquiriRouter


class OaiRouter(DaiquiriRouter):

    db = 'oai'
    app_label = 'daiquiri_oai'
