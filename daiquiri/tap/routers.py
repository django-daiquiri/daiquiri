from rest_framework.routers import Route, SimpleRouter


class SyncRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}$',
            mapping={'post': 'create'},
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        )
    ]
