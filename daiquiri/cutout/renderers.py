from daiquiri.core.renderers import ErrorRenderer


class CutOutErrorRenderer(ErrorRenderer):

    def render_votable(self, data, accepted_media_type=None, renderer_context=None):
        self.start('INFO', {
            'ID': 'Error',
            'name': 'Error',
            'value': self.get_error_string(data)
        })
        self.end('INFO')
