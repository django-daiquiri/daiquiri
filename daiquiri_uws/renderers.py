from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.six.moves import StringIO
from django.utils.encoding import smart_text

from rest_framework.renderers import BaseRenderer
from rest_framework.reverse import reverse


class UWSRenderer(BaseRenderer):

    media_type = 'application/xml'
    charset = 'utf-8'
    format = 'uws'

    ns_uws = 'http://www.ivoa.net/xml/UWS/v1.0'
    ns_xlink = 'http://www.w3.org/1999/xlink'
    ns_xsi = 'http://www.w3.org/2001/XMLSchema-instance'
    version = '1.1'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return ''

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()

        if isinstance(data, (list, tuple)):
            self._render_list(data, xml, renderer_context)
        elif isinstance(data, dict):
            self._render_detail(data, xml, renderer_context)

        xml.endDocument()
        return stream.getvalue()

    def _render_list(self, data, xml, renderer_context):
        xml.startElement('uws:jobs', {
            'xmlns:uws': self.ns_uws,
            'xmlns:xlink': self.ns_xlink,
            'version': self.version
        })

        for item in data:
            url_name = renderer_context['view'].detail_url_name
            href = reverse(url_name, args=[item['id']], request=renderer_context['request'])

            xml.startElement('uws:jobref', {
                'id': item['id'],
                'xlink:href': href,
                'xlink:type': 'simple'
            })

            xml.startElement('uws:phase', {})
            xml.characters(smart_text(item['phase']))
            xml.endElement('uws:phase')

            xml.endElement('uws:jobref')

        xml.endElement('uws:jobs')

    def _render_detail(self, data, xml, renderer_context):
        xml.startElement('uws:job', {
            'xmlns:uws': self.ns_uws,
            'xmlns:xsi': self.ns_xsi,
            'xmlns:xlink': self.ns_xlink,
            'version': self.version
        })

        for key in data:
            tag = 'uws:' + self._to_camel_case(key)

            if data[key] is None:
                xml.startElement(tag, {'xsi:nil': 'true'})
                xml.endElement(tag)
            else:
                xml.startElement(tag, {})
                xml.characters(smart_text(data[key]))
                xml.endElement(tag)

        xml.endElement('uws:job')

    def _to_camel_case(self, snake_str):
        components = snake_str.split('_')
        return components[0] + "".join(x.title() for x in components[1:])
