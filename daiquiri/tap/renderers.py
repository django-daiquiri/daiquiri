from daiquiri.core.utils import get_doi_url
from daiquiri.jobs.renderers import XMLRenderer


class AvailabilityRenderer(XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):

        self.start('vosi:availability', {
            'xmlns:vosi': 'http://www.ivoa.net/xml/VOSITables/v1.0',
            'xmlns:vs': 'http://www.ivoa.net/xml/VODataService/v1.0',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.ivoa.net/xml/VOSI/v1.0 http://www.ivoa.net/xml/VOSI/v1.0 http://www.ivoa.net/xml/VODataService/v1.0 http://www.ivoa.net/xml/VODataService/v1.0'
        })
        self.node('vosi:available', {}, data['available'])
        self.node('vosi:note', {}, data['note'])
        self.end('vosi:availability')


class CapabilitiesRenderer(XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):

        self.start('vosi:capabilities', {
            'xmlns:vosi': 'http://www.ivoa.net/xml/VOSITables/v1.0',
            'xmlns:vs': 'http://www.ivoa.net/xml/VODataService/v1.0',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.ivoa.net/xml/VOSI/v1.0 http://www.ivoa.net/xml/VOSI/v1.0 http://www.ivoa.net/xml/VODataService/v1.0 http://www.ivoa.net/xml/VODataService/v1.0'
        })

        for capability in data:

            self.start('vosi:capability', {'standardID': capability['schemaID']})

            self.start('interface', capability['interface']['attrs'])
            self.node('accessURL', capability['interface']['accessURL']['attrs'], capability['interface']['accessURL']['text'])
            self.end('interface')

            if 'languages' in capability:
                for language in capability['languages']:
                    self.start('language')
                    self.node('name', {}, language['name'])
                    self.node('version', {}, language['version'])
                    self.node('description', {}, language['description'])
                    self.end('language')

            self.end('vosi:capability')

        self.end('vosi:capabilities')


class TablesetRenderer(XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        self.start('vosi:tableset', {
            'xmlns:vosi': 'http://www.ivoa.net/xml/VOSITables/v1.0',
            'xmlns:vod': 'http://www.ivoa.net/xml/VODataService/v1.1',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.ivoa.net/xml/VODataService/v1.1 http://www.ivoa.net/xml/VOSITables/v1.0'
        })

        for schema in data:
            self.start('schema')
            self.node('name', {}, schema['name'])
            self.node('description', {}, schema['description'])

            for table in schema['tables']:
                table_attr = {}

                if table['doi']:
                    table_attr['doi'] = get_doi_url(table['doi'])

                if table['nrows'] is not None:
                    table_attr['size'] = str(table['nrows'])

                self.start('table', table_attr)
                self.node('name', {}, table['name'])
                self.node('description', {}, table['description'])

                for column in table['columns']:
                    self.start('column', {'std': 'true'} if column['std'] else {})
                    self.node('name', {}, column['name'])
                    self.node('dataType', {'xsi:type': 'vod:TAPType'}, column['datatype'])
                    self.node('ucd', {}, column['ucd'])
                    self.node('unit', {}, column['unit'])
                    for key in ['indexed', 'principal']:
                        if key in column and column[key]:
                            self.node('flag', {}, key)

                    self.end('column')

                self.end('table')

            self.end('schema')

        self.end('vosi:tableset')
