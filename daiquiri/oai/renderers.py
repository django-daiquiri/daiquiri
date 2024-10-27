from daiquiri.core.renderers import XMLRenderer
from daiquiri.core.renderers.datacite import DataciteRendererMixin
from daiquiri.core.renderers.dublincore import DublincoreRendererMixin
from daiquiri.core.renderers.voresource import VoresourceRendererMixin


class OaiRenderer(DublincoreRendererMixin, DataciteRendererMixin, VoresourceRendererMixin, XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        self.start('oai:OAI-PMH', {
            'xmlns:oai': 'http://www.openarchives.org/OAI/2.0/',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd'
        })
        self.node('oai:responseDate', {}, data['responseDate'])

        request_arguments = data['arguments']
        for error_code, _ in data['errors']:
            if error_code in ['badVerb', 'badArgument']:
                request_arguments = {}

        self.node('oai:request', request_arguments, data['baseUrl'])

        if data['errors']:
            self.render_errors(data['errors'])
        elif data['verb'] == 'GetRecord':
            self.render_get_record(data['response'])
        elif data['verb'] == 'Identify':
            self.render_identify(data['response'], data['baseUrl'])
        elif data['verb'] == 'ListIdentifiers':
            self.render_list_identifiers(data['response']['items'], data['response']['resumptionToken'])
        elif data['verb'] == 'ListMetadataFormats':
            self.render_list_metadata_formats(data['response'])
        elif data['verb'] == 'ListRecords':
            self.render_list_records(data['response']['items'], data['response']['resumptionToken'])
        elif data['verb'] == 'ListSets':
            self.render_list_sets(data['response'])

        self.end('oai:OAI-PMH')

    def render_errors(self, errors):
        for error_code, error_message in errors:
            self.node('error', {'code': error_code}, error_message)

    def render_get_record(self, item):
        self.start('oai:GetRecord')
        self.render_record(item)
        self.end('oai:GetRecord')

    def render_identify(self, repository_metadata, base_url):
        self.start('oai:Identify')
        self.node('oai:repositoryName', {}, repository_metadata.get('repository_name'))
        self.node('oai:baseURL', {}, base_url)
        self.node('oai:protocolVersion', {}, '2.0')
        self.node('oai:adminEmail', {}, repository_metadata['admin_email'])
        self.node('oai:earliestDatestamp', {}, repository_metadata.get('earliest_datestamp').strftime('%Y-%m-%dT%H:%M:%SZ'))  # noqa: E501
        self.node('oai:deletedRecord', {}, repository_metadata.get('deleted_record'))
        self.node('oai:granularity', {}, 'YYYY-MM-DDThh:mm:ssZ')
        self.render_identify_description(repository_metadata)
        self.end('oai:Identify')

    def render_identify_description(self, repository_metadata):
        self.start('oai:description')
        if repository_metadata['identifier'] is not None:
            self.render_oai_identifier(repository_metadata.get('identifier'))
        self.end('oai:description')

        self.start('oai:description')
        if repository_metadata['registry'] is not None:
            self.render_voresource(repository_metadata.get('registry'))
        self.end('oai:description')

    def render_oai_identifier(self, identifier_metadata):
        self.start('oai-identifier', {
            'xmlns': 'http://www.openarchives.org/OAI/2.0/oai-identifier',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.openarchives.org/OAI/2.0/oai-identifier http://www.openarchives.org/OAI/2.0/oai-identifier.xsd'
        })
        self.node('scheme', {}, identifier_metadata.get('scheme'))
        self.node('repositoryIdentifier', {}, identifier_metadata.get('repository_identifier'))
        self.node('delimiter', {}, identifier_metadata.get('delimiter'))
        self.node('sampleIdentifier', {}, identifier_metadata.get('sample_identifier'))
        self.end('oai-identifier')

    def render_list_identifiers(self, items, resumption_token):
        self.start('oai:ListIdentifiers')
        for item in items:
            self.render_header(item['header'])

        if resumption_token:
            self.node('oai:resumptionToken', {
                'oai:expirationDate': resumption_token.get('expirationDate'),
                'oai:completeListSize': resumption_token.get('completeListSize'),
                'oai:cursor': resumption_token.get('cursor')
            }, resumption_token['token'])

        self.end('oai:ListIdentifiers')

    def render_list_metadata_formats(self, metadata_formats):
        self.start('oai:ListMetadataFormats')
        for metadata_format in metadata_formats:
            self.start('oai:metadataFormat')
            self.node('oai:metadataPrefix', {}, metadata_format['prefix'])
            self.node('oai:schema', {}, metadata_format.get('schema'))
            self.node('oai:metadataNamespace', {}, metadata_format.get('namespace'))
            self.end('oai:metadataFormat')
        self.end('oai:ListMetadataFormats')

    def render_list_records(self, items, resumption_token):
        self.start('oai:ListRecords')
        for item in items:
            self.render_record(item)

        if resumption_token:
            self.node('oai:resumptionToken', {
                'oai:expirationDate': resumption_token.get('expirationDate'),
                'oai:completeListSize': resumption_token.get('completeListSize'),
                'oai:cursor': resumption_token.get('cursor')
            }, resumption_token['token'])

        self.end('oai:ListRecords')

    def render_list_sets(self, data):
        self.start('oai:ListSets')
        for oai_set in data['oai_sets']:
            self.start('oai:set')
            self.node('oai:setSpec', {}, oai_set['setSpec'])
            self.node('oai:setName', {}, oai_set['setName'])
            if oai_set['setDescription'] is not None:
                self.node('oai:setDescription', {}, oai_set['setDescription'])
            self.end('oai:set')
        self.end('oai:ListSets')

    def render_record(self, record):
        self.start('oai:record')
        self.render_header(record['header'])
        if record['metadata'] is not None:
            self.start('oai:metadata')
            self.render_metadata(record['metadata'])
            self.end('oai:metadata')
        self.end('oai:record')

    def render_header(self, header):
        self.start('oai:header', {'status': 'deleted'} if header['deleted'] else {})
        self.node('oai:identifier', {}, header['identifier'])
        self.node('oai:datestamp', {}, header['datestamp'])
        for spec in header.get('setSpec', []):
            self.node('oai:setSpec', {}, spec)
        self.end('oai:header')

    def render_metadata(self, metadata):
        raise NotImplementedError()


class DublincoreRenderer(OaiRenderer):

    def render_metadata(self, metadata):
        self.render_dublincore(metadata)


class OaiDataciteRenderer(OaiRenderer):

    def render_metadata(self, metadata):
        self.start('oai_datacite', {
            'xmlns': 'http://schema.datacite.org/oai/oai-1.0/',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://schema.datacite.org/oai/oai-1.0/ oai_datacite.xsd'
        })
        self.start('payload')
        self.render_datacite(metadata)
        self.end('payload')
        self.end('oai_datacite')


class DataciteRenderer(OaiRenderer):

    def render_metadata(self, metadata):
        self.render_datacite(metadata)


class VoresourceRenderer(OaiRenderer):

    def render_metadata(self, metadata):
        self.render_voresource(metadata)
