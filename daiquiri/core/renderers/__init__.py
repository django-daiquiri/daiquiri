import io

from django.utils.encoding import smart_str
from django.utils.xmlutils import SimplerXMLGenerator

from rest_framework.renderers import BaseRenderer


class XMLRenderer(BaseRenderer):

    media_type = 'application/xml'
    charset = 'utf-8'
    format = 'xml'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return ''

        stream = io.StringIO()

        self.xml = SimplerXMLGenerator(stream, self.charset)
        self.xml.startDocument()
        self.render_document(data, accepted_media_type, renderer_context)
        self.xml.endDocument()
        return stream.getvalue()

    def render_document(self, data, accepted_media_type=None, renderer_context=None):
        raise NotImplementedError()

    def start(self, tag, attrs={}):
        self.xml.startElement(tag, {k: v for k, v in attrs.items() if v is not None})

    def end(self, tag):
        self.xml.endElement(tag)

    def node(self, tag, attrs, text=''):
        if text is None:
            attrs.update({'xsi:nil': 'true'})

        self.xml.startElement(tag, {k: str(v) for k, v in attrs.items() if v is not None})
        if text is not None:
            self.xml.characters(smart_str(text))
        self.xml.endElement(tag)

    def _to_camel_case(self, snake_str):
        components = snake_str.split('_')
        return components[0] + "".join(x.title() for x in components[1:])


class VOTableRenderer(XMLRenderer):

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
                    errors.append('{}: {}'.format(parameter, ', '.join([str(e) for e in parameter_errors])))
                else:
                    errors.append(f'{parameter}: {parameter_errors}')
            return '\n'.join(errors)
        elif isinstance(data, (list, tuple)):
            return '\n'.join(data)
        else:
            return data
