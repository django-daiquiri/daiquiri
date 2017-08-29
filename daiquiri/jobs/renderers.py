from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.six.moves import StringIO
from django.utils.encoding import smart_text

from rest_framework.renderers import BaseRenderer

from .utils import get_job_url

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

    def start(self, tag, attr={}):
        self.xml.startElement(tag, attr)

    def end(self, tag):
        self.xml.endElement(tag)

    def node(self, tag, attr, text):
        if not text:
            attr.update({'xsi:nil': 'true'})
        self.xml.startElement(tag, attr)
        if text:
            self.xml.characters(smart_text(text))
        self.xml.endElement(tag)

    def _to_camel_case(self, snake_str):
        components = snake_str.split('_')
        return components[0] + "".join(x.title() for x in components[1:])


class UWSRenderer(XMLRenderer):

    root_attrs = {
        'xmlns:uws': 'http://www.ivoa.net/xml/UWS/v1.0',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink',
        'version': '1.1'
    }

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        request = renderer_context['request']

        if isinstance(data, dict):
            if list(data.keys()) == ['results']:
                self.render_results(data['results'], request, root=True)
            elif list(data.keys()) == ['parameters']:
                self.render_parameters(data['parameters'], request, root=True)
            else:
                self.render_job(data, request)
        else:
            self.render_jobs(data, request)

    def render_jobs(self, data, request):
        self.start('uws:jobs', self.root_attrs)

        for item in data:
            self.start('uws:jobref', {
                'id': item['id'],
                'xlink:href': get_job_url(request, kwargs={'pk': item['id']}),
                'xlink:type': 'simple'
            })
            self.node('uws:phase', {}, item['phase'])
            self.end('uws:jobref')

        self.end('uws:jobs')

    def render_job(self, data, request):
        self.start('uws:job', self.root_attrs)

        for key, value in data.items():
            if key == 'results':
                self.render_results(value, request)

            elif key == 'parameters':
                self.render_parameters(value, request)

            else:
                self.node('uws:' + self._to_camel_case(key), {}, value)

        self.end('uws:job')

    def render_results(self, data, request, root=False):
        self.start('uws:results', self.root_attrs if root else {})

        for format_key, url in data.items():
            self.start('uws:result', {
                'id': format_key,
                'xlink:href': request.build_absolute_uri(url),
                'xlink:type': format_key
            })
            self.end('uws:result')

        self.end('uws:results')

    def render_parameters(self, data, request, root=False):
        self.start('uws:parameters', self.root_attrs if root else {})

        for parameter_key, parameter_value in data.items():
            self.node('uws:parameter', {'id': parameter_key}, parameter_value)

        self.end('uws:parameters')


class VOTableRenderer(XMLRenderer):

    media_type = 'application/x-votable+xml'
    format = 'votable'

    root_attrs = {
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xmlns': 'http://www.ivoa.net/xml/VOTable/v1.3',
        'xmlns:stc': 'http://www.ivoa.net/xml/STC/v1.30'
    }

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        self.start('VOTABLE', self.root_attrs)
        self.render_votable(data)
        self.end('VOTABLE')

    def render_votable(self, data, accepted_media_type=None, renderer_context=None):
        raise NotImplementedError()


class ErrorRenderer(VOTableRenderer):

    def get_error_string(self, data):
        if isinstance(data, dict):
            errors = []
            for parameter, parameter_errors in data.items():
                if isinstance(parameter_errors, (list, tuple)):
                    errors.append('%s: %s' % (parameter, ', '.join(parameter_errors)))
                else:
                    errors.append('%s: %s' % (parameter, parameter_errors))
            return '\n'.join(errors)
        elif isinstance(data, (list, tuple)):
            return '\n'.join(data)
        else:
            return data


    def render_votable(self, data, accepted_media_type=None, renderer_context=None):
        self.start('RESOURCE', {
            'type': 'results'
        })
        self.node('INFO', {
            'name': 'QUERY_STATUS',
            'value': 'ERROR'
        }, self.get_error_string(data))
        self.end('RESOURCE')
