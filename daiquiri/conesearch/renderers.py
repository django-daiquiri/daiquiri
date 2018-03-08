from daiquiri.core.renderers import VOTableRenderer


class SearchRenderer(VOTableRenderer):

    def render_votable(self, data, accepted_media_type=None, renderer_context=None):
        self.start('RESOURCE', {
            'type': 'results'
        })
        self.node('INFO', {
            'name': 'QUERY_STATUS',
            'value': 'ERROR'
        }, 'test')
        self.end('RESOURCE')
