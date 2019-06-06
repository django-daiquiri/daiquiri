from daiquiri.oai.renderers import OaiRenderer


class DublincoreOaiRenderer(OaiRenderer):

    def render_metadata(self, metadata):
        self.start('oai_dc:dc', {
            'xmlns:oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
            'xmlns:dc': 'http://purl.org/dc/elements/1.1/',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd'
        })

        self.node('dc:title', {}, metadata['title'])

        creators = metadata['creators']
        if isinstance(creators, list):
            for creator in creators:
                self.node('dc:creator', {}, creator.get('name'))

        contributors = metadata['contributors']
        if isinstance(contributors, list):
            for contributor in contributors:
                self.node('dc:contributor', {}, contributor.get('name'))

        for subject in metadata['subjects']:
            self.node('dc:subject', {}, subject.get('subject'))

        self.node('dc:description', {}, metadata['description'])
        self.node('dc:date', {}, metadata['date'])
        self.node('dc:publisher', {}, metadata['publisher'])
        self.node('dc:identifier', {}, metadata['identifier'])

        self.end('oai_dc:dc')
