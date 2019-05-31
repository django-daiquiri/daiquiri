from daiquiri.core.renderers import XMLRenderer


class OAIPMHRenderer(XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):

        self.start('OAI-PMH', {
            'xmlns': 'http://www.openarchives.org/OAI/2.0/',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd'
        })
        self.node('responseDate', {}, data['response_date'])

        if data['errors']:
            request_args = {}
        else:
            request_args = {k: v for k, v in data['params'].items() if k != 'verb'}

        self.node('request', request_args, data['request'])

        if data['errors']:
            self.render_errors(data)
        elif data['params']['verb'] == 'GetRecord':
            self.render_get_record(data)
        elif data['params']['verb'] == 'Identify':
            self.render_identify(data)
        elif data['params']['verb'] == 'ListIdentifiers':
            self.render_list_identifiers(data)
        elif data['params']['verb'] == 'ListMetadataFormats':
            self.render_list_metadata_formats(data)
        elif data['params']['verb'] == 'ListRecords':
            self.render_list_records(data)
        elif data['params']['verb'] == 'ListSets':
            self.render_list_sets(data)

        self.end('OAI-PMH')

    def render_errors(self, data):
        for error_code, error_message in data['errors']:
            self.node('error', {'code': error_code}, error_message)

    def render_get_record(self, data):
        self.start('GetRecord')

        self.end('GetRecord')

    def render_identify(self, data):
        self.start('Identify')

        self.end('Identify')

    def render_list_identifiers(self, data):
        self.start('ListIdentifiers')

        self.end('ListIdentifiers')

    def render_list_metadata_formats(self, data):
        self.start('ListIdentifiers')

        self.end('ListIdentifiers')

    def render_list_records(self, data):
        self.start('ListRecords')

        self.end('ListRecords')

    def render_list_sets(self, data):
        self.start('ListSets')

        self.end('ListSets')
