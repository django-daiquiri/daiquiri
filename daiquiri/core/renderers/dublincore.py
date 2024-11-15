class DublincoreRendererMixin:

    def render_dublincore(self, metadata):
        self.start('oai_dc:dc', {
            'xmlns:oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
            'xmlns:dc': 'http://purl.org/dc/elements/1.1/',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd'
        })

        self.node('dc:identifier', {}, metadata.get('identifier'))
        self.node('dc:title', {}, metadata.get('title'))

        creators = metadata.get('creators')
        if isinstance(creators, list):
            for creator in creators:
                self.node('dc:creator', {}, creator.get('name'))

        contributors = metadata.get('contributors')
        if isinstance(contributors, list):
            for contributor in contributors:
                self.node('dc:contributor', {}, contributor.get('name'))

        for subject in metadata.get('subjects', []):
            self.node('dc:subject', {}, subject.get('subject'))

        self.node('dc:publisher', {}, metadata.get('publisher'))

        if metadata.get('description'):
            self.node('dc:description', {}, metadata.get('description'))
        if metadata.get('date'):
            self.node('dc:date', {}, metadata.get('date'))
        if metadata.get('rights'):
            self.node('dc:rights', {}, metadata.get('rights'))
        if metadata.get('type'):
            self.node('dc:type', {}, metadata.get('type'))

        self.end('oai_dc:dc')
