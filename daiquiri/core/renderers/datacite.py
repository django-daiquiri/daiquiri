class DataciteRendererMixin:

    def render_datacite(self, metadata):
        self.start('resource', {
            'xmlns': 'http://datacite.org/schema/kernel-4',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.6/metadata.xsd'
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

        self.node('publisher', metadata.get('publisher_properties', {}), metadata.get('publisher'))
        self.node('publicationYear', {}, metadata.get('publication_year'))

        self.start('subjects')
        for subject in metadata.get('subjects', []):
            self.node('subject', {
                'xml:lang': 'en',
                'subjectScheme': subject.get('subjectScheme'),
                'schemeURI': subject.get('schemeURI'),
                'valueURI': subject.get('valueURI')
            }, subject.get('subject'))
        self.end('subjects')

        self.start('contributors')
        contributors = metadata.get('contributors', [])
        if isinstance(contributors, list):
            for contributor in contributors:
                self.render_person('contributor', contributor, contributor.get('contributor_type', 'DataManager'))
        self.end('contributors')

        updated = metadata.get('updated')
        published = metadata.get('published')
        if updated is not None or published is not None:
            self.start('dates')
            if updated:
                self.node('date', {'dateType': 'Updated'}, updated)
            if published:
                self.node('date', {'dateType': 'Issued'}, published)
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

        alternate_identifiers = metadata.get('alternate_identifiers')
        if alternate_identifiers is not None:
            self.start('alternateIdentifiers')
            for alternate_identifier in alternate_identifiers:
                self.node('alternateIdentifier', {
                    'alternateIdentifierType': alternate_identifier.get('alternate_identifier_type')
                }, alternate_identifier.get('alternate_identifier'))
            self.end('alternateIdentifiers')

        sizes = metadata.get('sizes')
        if sizes is not None:
            self.start('sizes')
            for size in sizes:
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
            self.node('rights', {
                'rightsURI': metadata.get('license_url'),
                'rightsIdentifier': metadata.get('license_identifier'),
                },
                metadata.get('license_label'))
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

    def render_person(self, person_type, person, contributor_type=None):
        if isinstance(person, dict):
            self.start(person_type, {
                'contributorType': contributor_type
            })

            name = person.get('name')
            first_name = person.get('first_name')
            last_name = person.get('last_name')
            name_type = person.get('name_type')

            if not name:
                name = f'{last_name}, {first_name}'

            self.node(person_type + 'Name', {'nameType': name_type}, name)

            if first_name:
                self.node('givenName', {}, first_name)

            if last_name:
                self.node('familyName', {}, last_name)

            orcid = person.get('orcid')
            if orcid:
                self.node('nameIdentifier', {
                    'schemeURI': 'http://orcid.org/',
                    'nameIdentifierScheme': 'ORCID'
                }, orcid)

            ror = person.get('ror')
            if ror:
                self.node('nameIdentifier', {
                    'schemeURI': 'http://ror.org/',
                    'nameIdentifierScheme': 'ROR'
                }, ror)

            affiliations = person.get('affiliations')
            if affiliations:
                for affiliation in affiliations:
                    self.node('affiliation', {
                        'affiliationIdentifier': affiliation.get('affiliation_identifier'),
                        'affiliationIdentifierScheme': affiliation.get('affiliation_identifier_scheme'),
                        'schemeURI': affiliation.get('scheme_uri')
                        }, affiliation.get('affiliation'))

            self.end(person_type)
