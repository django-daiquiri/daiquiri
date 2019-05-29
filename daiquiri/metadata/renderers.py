from daiquiri.jobs.renderers import XMLRenderer


class DataCiteRenderer(XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):

        self.start('resource', {
            'xmlns': 'http://datacite.org/schema/kernel-4',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.1/metadata.xsd'
        })
        self.node('identifier', {'identifierType': 'DOI'}, data.get('doi'))

        self.start('creators')
        for creator in data.get('creator', []):
            self.start('creator')
            self.node('creatorName', {}, data.get('name'))
            self.node('givenName', {}, data.get('first_name'))
            self.node('familyName', {}, data.get('last_name'))
            self.node('nameIdentifier', {
                'schemeURI': 'http://orcid.org/',
                'nameIdentifierScheme': 'ORCID'
            }, data.get('orcid'))
            self.node('affiliation', {}, creator.get('affiliation'))
            self.end('creator')
        self.end('creators')

        self.start('titles')
        self.node('title', {'xml:lang': 'en'}, data.get('title') or data.get('name'))
        self.end('titles')

        self.node('publisher', {}, data.get('publisher'))
        self.node('publicationYear', {}, data.get('publication_year'))

        subjects = data.get('subjects')
        if subjects is not None:
            self.start('subjects')
            for subject in subjects:
                self.node('subject', {
                    'xml:lang': 'en',
                    'schemeURI': subject.get('scheme_uri'),
                    'subjectScheme': subject.get('subject_scheme')
                }, subject.get('subject'))
            self.end('subjects')

        updated = data.get('updated')
        if updated is not None:
            self.start('dates')
            self.node('data', {'dateType': 'Updated'}, updated)
            self.end('dates')

        language = data.get('language')
        if language is not None:
            self.node('language', {}, language)

        self.node('resourceType', {'resourceTypeGeneral': 'Dataset'}, data.get('resource_type'))

        related_identifiers = data.get('related_identifiers')
        if related_identifiers is not None:
            self.start('relatedIdentifiers')
            for related_identifier in related_identifiers:
                self.node('relatedIdentifier', {
                    'relatedIdentifierType': related_identifier.get('related_identifier_type'),
                    'relationType': related_identifier.get('relation_type')
                }, subject.get('related_identifier'))
            self.end('relatedIdentifiers')

        size = data.get('size')
        if size is not None:
            self.start('sizes')
            self.node('size', {}, size)
            self.end('sizes')

        formats = data.get('formats')
        if formats is not None:
            self.start('formats')
            for format in formats:
                self.node('format', {}, format)
            self.end('formats')

        version = data.get('version')
        if version is not None:
            self.node('version', {}, version)

        license = data.get('license')
        if license is not None:
            self.start('rightsList')
            self.node('rights', {'rightsURI': data.get('license_url')}, license)
            self.end('rightsList')

        description = data.get('long_description') or data.get('description')
        if description is not None:
            self.start('descriptions')
            self.node('description', {
                'xml:lang': data.get('language'),
                'descriptionType': 'Abstract'
            }, description)
            self.end('descriptions')

        self.end('resource')
