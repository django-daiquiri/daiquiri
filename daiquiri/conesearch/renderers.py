from django.conf import settings

from daiquiri.core.renderers import VOTableRenderer


class SearchRenderer(VOTableRenderer):

    def render_votable(self, data, accepted_media_type=None, renderer_context=None):
        self.start('RESOURCE', {
            'type': 'results'
        })

        self.start('TABLE')

        for column in settings.CONESEARCH_COLUMNS:
            self.start('FIELD', column)
            self.end('FIELD')

        self.start('DATA')
        self.start('TABLEDATA')
        for row in data['rows']:
            self.start('TR')
            for cell in row:
                self.node('TD', {}, cell)
            self.end('TR')
        self.end('TABLEDATA')
        self.end('DATA')

        self.end('TABLE')
        self.end('RESOURCE')
