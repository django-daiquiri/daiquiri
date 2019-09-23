from daiquiri.core.renderers import XMLRenderer
from daiquiri.core.renderers.dublincore import DublincoreRendererMixin
from daiquiri.core.renderers.datacite import DataciteRendererMixin
from daiquiri.core.renderers.voresource import VoresourceRendererMixin


class OaiRenderer(DublincoreRendererMixin, DataciteRendererMixin, VoresourceRendererMixin, XMLRenderer):

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
            self.render_list_identifiers(data['response']['items'], data['response']['resumptionToken'])
        elif data['verb'] == 'ListMetadataFormats':
            self.render_list_metadata_formats(data['response'])
        elif data['verb'] == 'ListRecords':
            self.render_list_records(data['response']['items'], data['response']['resumptionToken'])
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
        self.node('repositoryName', {}, repository_metadata['repository_name'])
        self.node('baseUrl', {}, base_url)
        self.node('protocolVersion', {}, '2.0')
        for email in repository_metadata['admin_emails']:
            self.node('adminEmail', {}, email)
        self.node('earliestDatestamp', {}, repository_metadata['earliest_datestamp'])
        self.node('deletedRecord', {}, repository_metadata['deleted_record'])
        self.node('granularity', {}, repository_metadata['granularity'])
        self.render_identify_description(repository_metadata)
        self.end('Identify')

    def render_identify_description(self, repository_metadata):
        self.start('description')
        self.render_oai_identifier(repository_metadata['identifier'])
        self.render_voresource(repository_metadata['registry'])
        self.end('description')

    def render_oai_identifier(self, identifier_metadata):
        self.start('oai-identifier', {
            'xmlns': 'http://www.openarchives.org/OAI/2.0/oai-identifier',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.openarchives.org/OAI/2.0/oai-identifier http://www.openarchives.org/OAI/2.0/oai-identifier.xsd'
        })
        self.node('scheme', {}, identifier_metadata.get('scheme'))
        if identifier_metadata.get('repository_identifier'):
            self.node('repositoryIdentifier', {}, identifier_metadata.get('repository_identifier'))
        self.node('delimiter', {}, identifier_metadata.get('delimiter'))
        self.end('oai-identifier')

    def render_list_identifiers(self, items, resumption_token):
        self.start('ListIdentifiers')
        for item in items:
            self.render_header(item['header'])

        if resumption_token:
            self.node('resumptionToken', {
                'expirationDate': resumption_token.get('expirationDate'),
                'completeListSize': resumption_token.get('completeListSize'),
                'cursor': resumption_token.get('cursor')
            }, resumption_token['token'])

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

    def render_list_records(self, items, resumption_token):
        self.start('ListRecords')
        for item in items:
            self.render_record(item)

        if resumption_token:
            self.node('resumptionToken', {
                'expirationDate': resumption_token.get('expirationDate'),
                'completeListSize': resumption_token.get('completeListSize'),
                'cursor': resumption_token.get('cursor')
            }, resumption_token['token'])

        self.end('ListRecords')

    def render_list_sets(self, data):
        self.start('ListSets')
        self.end('ListSets')

    def render_record(self, record):
        self.start('record')
        self.render_header(record['header'])
        if record['metadata'] is not None:
            self.start('metadata')
            self.render_metadata(record['metadata'])
            self.end('metadata')
        self.end('record')

    def render_header(self, header):
        self.start('header', {'status': 'deleted'} if header['deleted'] else {})
        self.node('identifier', {}, header['identifier'])
        self.node('datestamp', {}, header['datestamp'])
        self.end('header')

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
