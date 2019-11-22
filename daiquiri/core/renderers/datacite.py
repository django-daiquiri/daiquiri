class DataciteRendererMixin(object):

    def render_datacite(self, metadata):
        self.start('resource', {
            'xmlns': 'http://datacite.org/schema/kernel-4',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.1/metadata.xsd'
        })
        self.node('identifier', {'identifierType': 'DOI'}, metadata.get('identifier'))

        self.start('creators')
        creators = metadata.get('creators', [])
        if isinstance(creators, list):
            for creator in creators:
                self.render_person('creator', creator)
        self.end('creators')

        self.start('titles')
        self.node('title', {'xml:lang': 'en'}, metadata.get('title'))
        self.end('titles')

        self.node('publisher', {}, metadata.get('publisher'))
        self.node('publicationYear', {}, metadata.get('publication_year'))

        self.start('subjects')
        for subject in metadata.get('subjects', []):
            self.node('subject', {
                'xml:lang': 'en',
                'schemeURI': subject.get('scheme_uri'),
                'subjectScheme': subject.get('subject_scheme')
            }, subject.get('subject'))
        self.end('subjects')

        self.start('contributors')
        contributors = metadata.get('contributors', [])
        if isinstance(contributors, list):
            for contributor in contributors:
                self.render_person('contributor', contributor)
        self.end('contributors')

        updated = metadata.get('updated')
        if updated is not None:
            self.start('dates')
            self.node('date', {'dateType': 'Updated'}, updated)
            self.end('dates')

        self.node('language', {}, metadata.get('language'))
        self.node('resourceType', {'resourceTypeGeneral': 'Dataset'}, metadata.get('resource_type'))

        related_identifiers = metadata.get('related_identifiers')
        if related_identifiers is not None:
            self.start('relatedIdentifiers')
            for related_identifier in related_identifiers:
                self.node('relatedIdentifier', {
                    'relatedIdentifierType': related_identifier.get('related_identifier_type'),
                    'relationType': related_identifier.get('relation_type')
                }, related_identifier.get('related_identifier'))
            self.end('relatedIdentifiers')

        size = metadata.get('size')
        if size is not None:
            self.start('sizes')
            self.node('size', {}, size)
            self.end('sizes')

        formats = metadata.get('formats')
        if formats is not None:
            self.start('formats')
            for format in formats:
                self.node('format', {}, format)
            self.end('formats')

        version = metadata.get('version')
        if version is not None:
            self.node('version', {}, version)

        license = metadata.get('license')
        if license is not None:
            self.start('rightsList')
            self.node('rights', {'rightsURI': metadata.get('license_url')}, license)
            self.end('rightsList')

        description = metadata.get('long_description') or metadata.get('description')
        if description is not None:
            self.start('descriptions')
            self.node('description', {
                'xml:lang': metadata.get('language'),
                'descriptionType': 'Abstract'
            }, description)
            self.end('descriptions')

        self.end('resource')

    def render_person(self, person_type, person):
        if isinstance(person, dict):
            self.start(person_type)

            name = person.get('name')
            if name:
                self.node(person_type + 'Name', {}, name)

            first_name = person.get('first_name')
            if first_name:
                self.node('first_name', {}, first_name)

            last_name = person.get('last_name')
            if last_name:
                self.node('last_name', {}, last_name)

            orcid = person.get('orcid')
            if orcid:
                self.node('nameIdentifier', {
                    'schemeURI': 'http://orcid.org/',
                    'nameIdentifierScheme': 'ORCID'
                }, orcid)

            affiliations = person.get('affiliations')
            if affiliations:
                for affiliation in affiliations.splitlines():
                    self.node('affiliation', {}, affiliation)

            self.end(person_type)
