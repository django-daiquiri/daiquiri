from daiquiri.core.renderers import XMLRenderer


class OaiRenderer(XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        self.start('OAI-PMH', {
            'xmlns': 'http://www.openarchives.org/OAI/2.0/',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd'
        })
        self.node('responseDate', {}, data['responseDate'])

        request_arguments = data['arguments']
        for error_code, _ in data['errors']:
            if error_code in ['badVerb', 'badArgument']:
                request_arguments = {}

        self.node('request', request_arguments, data['baseUrl'])

        if data['errors']:
            self.render_errors(data['errors'])
        elif data['verb'] == 'GetRecord':
            self.render_get_record(data['response'])
        elif data['verb'] == 'Identify':
            self.render_identify(data['response'], data['baseUrl'])
        elif data['verb'] == 'ListIdentifiers':
            self.render_list_identifiers(data['response'])
        elif data['verb'] == 'ListMetadataFormats':
            self.render_list_metadata_formats(data['response'])
        elif data['verb'] == 'ListRecords':
            self.render_list_records(data['response'])
        elif data['verb'] == 'ListSets':
            self.render_list_sets(data['response'])

        self.end('OAI-PMH')

    def render_errors(self, errors):
        for error_code, error_message in errors:
            self.node('error', {'code': error_code}, error_message)

    def render_get_record(self, item):
        self.start('GetRecord')
        self.render_record(item)
        self.end('GetRecord')

    def render_identify(self, repository_metadata, base_url):
        self.start('Identify')
        self.node('repositoryName', {}, repository_metadata['repositoryName'])
        self.node('baseUrl', {}, base_url)
        self.node('protocolVersion', {}, '2.0')
        for email in repository_metadata['adminEmails']:
            self.node('adminEmail', {}, email)
        self.node('earliestDatestamp', {}, repository_metadata['earliestDatestamp'])
        self.node('deletedRecord', {}, repository_metadata['deletedRecord'])
        self.node('granularity', {}, repository_metadata['granularity'])
        self.start('description')
        self.start('oai-identifier', {
            'xmlns': 'http://www.openarchives.org/OAI/2.0/oai-identifier',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.openarchives.org/OAI/2.0/oai-identifier http://www.openarchives.org/OAI/2.0/oai-identifier.xsd'
        })
        self.node('scheme', {}, repository_metadata['identifier']['scheme'])
        self.node('repositoryIdentifier', {}, repository_metadata['identifier']['repositoryIdentifier'])
        self.node('delimiter', {}, repository_metadata['identifier']['delimiter'])
        self.end('oai-identifier')
        self.end('description')
        self.end('Identify')

    def render_list_identifiers(self, items):
        self.start('ListIdentifiers')
        for item in items:
            self.start('header')
            self.node('identifier', {}, item['identifier'])
            self.node('datestamp', {}, item['datestamp'])
            self.end('header')
        self.end('ListIdentifiers')

    def render_list_metadata_formats(self, metadata_formats):
        self.start('ListMetadataFormats')
        for metadata_format in metadata_formats:
            self.start('metadataFormat')
            self.node('metadataPrefix', {}, metadata_format['prefix'])
            self.node('schema', {}, metadata_format.get('schema'))
            self.node('metadataNamespace', {}, metadata_format.get('namespace'))
            self.end('metadataFormat')
        self.end('ListMetadataFormats')

    def render_list_records(self, items):
        self.start('ListRecords')
        for item in items:
            self.render_record(item)
        self.end('ListRecords')

    def render_list_sets(self, data):
        self.start('ListSets')
        self.end('ListSets')

    def render_record(self, record):
        self.start('record')
        self.start('header')
        self.node('identifier', {}, record['identifier'])
        self.node('datestamp', {}, record['datestamp'])
        self.end('header')
        self.start('metadata')
        self.render_metadata(record['metadata'])
        self.end('metadata')
        self.end('record')

    def render_metadata(self, metadata):
        raise NotImplementedError()
