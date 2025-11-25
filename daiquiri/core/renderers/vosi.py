from daiquiri.core.renderers import XMLRenderer
from daiquiri.core.utils import get_doi_url


class AvailabilityRenderer(XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        self.start('vosi:availability', {
            'xmlns:vosi': 'http://www.ivoa.net/xml/VOSITables/v1.0',
            'xmlns:vs': 'http://www.ivoa.net/xml/VODataService/v1.0',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.ivoa.net/xml/VOSI/v1.0 http://www.ivoa.net/xml/VOSI/v1.0 http://www.ivoa.net/xml/VODataService/v1.0 http://www.ivoa.net/xml/VODataService/v1.0'  # noqa: E501
        })
        self.node('available', {}, data.get('available'))
        self.node('note', {}, data.get('note'))
        self.end('vosi:availability')


class CapabilitiesRendererMixin:

    def render_capability(self, capability):
        self.start('capability', {
            'standardID': capability.get('id'),
            'xsi:type': capability.get('type')
        })

        interface = capability.get('interface')
        if interface:
            self.start('interface', {
                'role': interface.get('role'),
                'version': interface.get('version'),
                'xsi:type': interface.get('type')
            })
            access_url = interface.get('access_url')
            if access_url:
                self.node('accessURL', {
                    'use': access_url.get('use'),
                }, access_url.get('url'))

            query_types = interface.get('query_types')
            if query_types:
                for query_type in query_types:
                    self.node('queryType', {}, query_type)

            if interface.get('result_type'):
                self.node('resultType', {}, interface.get('result_type'))

            params = interface.get('params', [])
            for param in params:
                self.start('param', {
                    'std': param.get('std'),
                    'use': param.get('use')
                })
                self.node('name', {}, param.get('name'))
                self.node('description', {}, param.get('description'))

                if param.get('unit'):
                    self.node('unit', {}, param.get('unit'))
                if param.get('ucd'):
                    self.node('ucd', {}, param.get('ucd'))
                self.node('dataType', {}, param.get('datatype'))
                self.end('param')
            self.end('interface')

        for language in capability.get('languages', []):
            self.start('language')
            self.node('name', {}, language.get('name'))
            self.node('version', {}, language.get('version'))
            self.node('description', {}, language.get('description'))
            self.end('language')

        for output_format in capability.get('output_formats', []):
            self.start('outputFormat')
            self.node('mime', {}, output_format.get('mime'))
            self.node('alias', {}, output_format.get('alias'))
            self.end('outputFormat')

        if capability.get('max_sr'):
            self.node('maxSR', {}, capability.get('max_sr'))

        if capability.get('max_records'):
            self.node('maxRecords', {}, capability.get('max_records'))

        if capability.get('verbosity'):
            self.node('verbosity', {}, capability.get('verbosity'))

        for upload_method in capability.get('upload_methods', []):
            self.node('uploadMethod', {'ivo-id': upload_method})

        if capability.get('output_limit'):
            self.start('outputLimit')
            self.node('default', {'unit': 'row'}, capability.get('output_limit'))
            self.node('hard', {'unit': 'row'}, capability.get('output_limit'))
            self.end('outputLimit')

        if capability.get('upload_limit'):
            self.start('uploadLimit')
            self.node('hard', {'unit': 'byte'}, capability.get('upload_limit'))
            self.end('uploadLimit')

        test_query = capability.get('test_query')
        if test_query:
            self.start('testQuery')
            self.node('ra', {}, test_query.get('ra'))
            self.node('dec', {}, test_query.get('dec'))
            self.node('sr', {}, test_query.get('sr'))
            self.end('testQuery')

        self.end('capability')


class CapabilitiesRenderer(CapabilitiesRendererMixin, XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        ns = {
            'xmlns:cap': 'http://www.ivoa.net/xml/VOSICapabilities/v1.0',
            'xmlns:vosi': 'http://www.ivoa.net/xml/VOSITables/v1.0',
            'xmlns:tr': 'http://www.ivoa.net/xml/TAPRegExt/v1.0',
            'xmlns:vr': 'http://www.ivoa.net/xml/VOResource/v1.0',
            'xmlns:vs': 'http://www.ivoa.net/xml/VODataService/v1.1',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        }
        ns['xsi:schemaLocation'] = ' '.join(ns.values())

        self.start('vosi:capabilities', ns)

        for capability in data:
            self.render_capability(capability)

        self.end('vosi:capabilities')


class TablesetRendererMixin:

    def render_tableset(self, tableset, strict=False):
        for schema in tableset:
            self.start('schema')
            self.node('name', {}, schema.get('name'))
            self.node('description', {}, schema.get('description') or '')

            for table in schema.get('tables'):
                if strict:
                    self.start('table')
                else:
                    self.start('table', {
                        'doi': get_doi_url(table.get('doi')),
                        'size': str(table.get('nrows'))
                    })
                self.node('name', {}, table.get('name'))
                self.node('description', {}, table.get('description') or '')

                for column in table['columns']:
                    self.start('column', {'std': 'true'} if column['std'] else {})
                    self.node('name', {}, column['name'])
                    self.node('description', {}, column.get('description') or '')
                    self.node('unit', {}, column.get('unit') or '')
                    self.node('ucd', {}, column.get('ucd') or '')

                    self.render_datatype(column.get('datatype'))
                    for key in ['indexed', 'principal']:
                        if key in column and column.get('key'):
                            self.node('flag', {}, key)

                    self.end('column')

                self.end('table')

            self.end('schema')

    def render_datatype(self, datatype):
        if datatype in ['boolean', 'bit', 'unsignedByte', 'short', 'int', 'long', 'char', 'unicodeChar',
                        'float', 'double', 'floatComplex', 'doubleComplex']:
            self.node('dataType', {'xsi:type': 'vs:VOTableType'}, datatype)
        elif datatype == 'timestamp':
            self.node('dataType', {'xsi:type': 'vs:VOTableType', 'extendedType': 'timestamp'}, 'char')
        else:
            self.node('dataType', {'xsi:type': 'vs:VOTableType'}, 'char')


class TablesetRenderer(TablesetRendererMixin, XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        self.start('vosi:tableset', {
            'xmlns:vosi': 'http://www.ivoa.net/xml/VOSITables/v1.0',
            'xmlns:vs': 'http://www.ivoa.net/xml/VODataService/v1.1',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.ivoa.net/xml/VODataService/v1.1 http://www.ivoa.net/xml/VOSITables/v1.0'
        })
        self.render_tableset(data)
        self.end('vosi:tableset')
