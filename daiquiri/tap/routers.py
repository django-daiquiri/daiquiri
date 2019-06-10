from daiquiri.core.routers import DaiquiriRouter


class TapRouter(DaiquiriRouter):

    db = 'tap'
    app_label = 'daiquiri_tap'
