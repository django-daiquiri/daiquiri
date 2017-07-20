from daiquiri.dali.renderers import XMLRenderer


class ExampleRenderer(XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):

        self.start('div', {
            'vocab': 'http://www.ivoa.net/rdf/examples',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        })
        for example in data:
            self.start('div', {
                'id': 'example-%i' % example['id'],
                'resource': '#example-%i' % example['id'],
                'typeof': 'example'
            })
            self.node('h2', {'property': 'name'}, example['name'])
            self.node('p', {'property': 'capability'}, 'ivo://ivoa.net/std/TAP')
            self.node('p', {'property': 'description'}, example['description'])
            self.node('pre', {'property': 'query'}, example['query_string'])
            self.end('div')

        self.end('div')

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
            self.start('vosi:schema')
            self.node('name', {}, schema['schema_name'])
            self.node('description', {}, schema['description'])

            for table in schema['tables']:
                self.start('vosi:table')
                self.node('name', {}, table['table_name'])
                self.node('description', {}, table['description'])

                for column in table['columns']:
                    self.start('vosi:column')
                    self.node('name', {}, column['column_name'])
                    self.node('dataType', {'xsi:type': 'vod:TAPType'}, column['datatype'])
                    self.node('ucd', {}, column['ucd'])
                    if 'indexed' in column and column['indexed']:
                        self.node('flag', {}, 'indexed')
                    if 'primary' in column and column['primary']:
                        self.node('flag', {}, 'primary')
                    if 'std' in column and column['std']:
                        self.node('flag', {}, 'std')
                    self.end('vosi:column')

                self.end('vosi:table')

            self.end('vosi:schema')

        self.end('vosi:tableset')
