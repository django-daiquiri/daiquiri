from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.six.moves import StringIO
from django.utils.encoding import smart_text

from rest_framework.renderers import BaseRenderer
from rest_framework.reverse import reverse


class XMLRenderer(BaseRenderer):

    media_type = 'application/xml'
    charset = 'utf-8'
    format = 'xml'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return ''

        stream = StringIO()

        self.xml = SimplerXMLGenerator(stream, self.charset)
        self.xml.startDocument()
        self.render_document(data, accepted_media_type, renderer_context)
        self.xml.endDocument()
        return stream.getvalue()

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        raise NotImplementedError()

    def render_text_node(self, tag, attr, text):
        self.xml.startElement(tag, attr)
        self.xml.characters(smart_text(text))
        self.xml.endElement(tag)

    def render_empty_node(self, tag, attr):
        self.xml.startElement(tag, attr)
        self.xml.endElement(tag)

    def render_nil_node(self, tag, attr):
        attr.update({'xsi:nil': 'true'})
        self.xml.startElement(tag, attr)
        self.xml.endElement(tag)

    def _to_camel_case(self, snake_str):
        components = snake_str.split('_')
        return components[0] + "".join(x.title() for x in components[1:])


class UWSRenderer(XMLRenderer):

    media_type = 'application/xml'
    format = 'uws'

    root_attrs = {
        'xmlns:uws': 'http://www.ivoa.net/xml/UWS/v1.0',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink',
        'version': '1.1'
    }

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        if data:
            request = renderer_context['request']

            if isinstance(data, dict):
                if data.keys() == ['results']:
                    self.render_results(data['results'], request, root=True)
                elif data.keys() == ['parameters']:
                    self.render_parameters(data['parameters'], request, root=True)
                else:
                    self.render_job(data, request)
            else:
                self.render_jobs(data, request)

    def render_jobs(self, data, request):
        self.xml.startElement('uws:jobs', self.root_attrs)

        for item in data:
            base_name = request.resolver_match.url_name.rsplit('-', 1)[0]
            href = reverse(base_name + '-detail', args=[item['id']], request=request)

            self.xml.startElement('uws:jobref', {
                'id': item['id'],
                'xlink:href': href,
                'xlink:type': 'simple'
            })
            self.render_text_node('uws:phase', {}, item['phase'])
            self.xml.endElement('uws:jobref')

        self.xml.endElement('uws:jobs')

    def render_job(self, data, request):
        self.xml.startElement('uws:job', self.root_attrs)

        for key, value in data.items():
            if key == 'results':
                self.render_results(value, request)

            elif key == 'parameters':
                self.render_parameters(value, request)

            else:
                tag = 'uws:' + self._to_camel_case(key)

                if value is None:
                    self.render_nil_node(tag, {})
                else:
                    self.render_text_node(tag, {}, value)

        self.xml.endElement('uws:job')

    def render_results(self, data, request, root=False):
        self.xml.startElement('uws:results', self.root_attrs if root else {})

        for format_key, url in data.items():
            self.render_empty_node('uws:result', {
                'id': format_key,
                'xlink:href': request.build_absolute_uri(url),
                'xlink:type': format_key
            })

        self.xml.endElement('uws:results')

    def render_parameters(self, data, request, root=False):
        self.xml.startElement('uws:parameters', self.root_attrs if root else {})

        for parameter_key, parameter_value in data.items():
            if parameter_value is None:
                self.render_nil_node('uws:parameter', {'id': parameter_key})
            else:
                self.render_text_node('uws:parameter', {'id': parameter_key}, parameter_value)

        self.xml.endElement('uws:parameters')


class VOTableRenderer(XMLRenderer):

    media_type = 'application/x-votable+xml'
    format = 'votable'

    root_attrs = {
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xmlns': 'http://www.ivoa.net/xml/VOTable/v1.3',
        'xmlns:stc': 'http://www.ivoa.net/xml/STC/v1.30'
    }

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        self.xml.startElement('VOTABLE', self.root_attrs)
        self.render_votable(data)
        self.xml.endElement('VOTABLE')

    def render_votable(self, data, accepted_media_type=None, renderer_context=None):
        raise NotImplementedError()


class ErrorRenderer(VOTableRenderer):

    def get_error_string(self, data):
        errors = []
        for parameter, parameter_errors in data.items():
            if isinstance(parameter_errors, (list, tuple)):
                errors.append('%s: %s' % (parameter, ', '.join(parameter_errors)))
            else:
                errors.append('%s: %s' % (parameter, parameter_errors))

        return '\n'.join(errors)

    def render_votable(self, data, accepted_media_type=None, renderer_context=None):
        self.xml.startElement('RESOURCE', {
            'type': 'results'
        })
        self.render_text_node('INFO', {
            'name': 'QUERY_STATUS',
            'value': 'ERROR'
        }, self.get_error_string(data))
        self.xml.endElement('RESOURCE')


class TablesetRenderer(XMLRenderer):

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        self.xml.startElement('vosi:tableset', {
            'xmlns:vosi': 'http://www.ivoa.net/xml/VOSITables/v1.0',
            'xmlns:vod': 'http://www.ivoa.net/xml/VODataService/v1.1',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.ivoa.net/xml/VODataService/v1.1 http://www.ivoa.net/xml/VOSITables/v1.0'
        })

        for schema in data['schemas']:
            self.xml.startElement('vosi:schema')
            self.render_text_node('name', {}, schema.schema_name)
            self.render_text_node('description', {}, schema.description)

            for table in schema['tables']:
                self.xml.startElement('vosi:table')
                self.render_text_node('name', {}, table.table_name)
                self.render_text_node('description', {}, table.description)

                for column in table['columns']:
                    self.xml.startElement('vosi:column')
                    self.render_text_node('name', {}, column.column_name)
                    self.render_text_node('dataType', {'xsi:type': 'vod:TAPType'}, column.datatype)
                    self.render_text_node('ucd', {}, column.ucd)
                    if column.indexed:
                        self.render_text_node('flag', {}, 'indexed')
                    if column.primary:
                        self.render_text_node('flag', {}, 'primary')
                    if column.std:
                        self.render_text_node('flag', {}, 'std')
                    self.xml.endElement('vosi:column')

                self.xml.endElement('vosi:table')

            self.xml.endElement('vosi:schema')

        self.xml.endElement('vosi:tableset')
