from daiquiri.core.renderers import ErrorRenderer, XMLRenderer

from .utils import get_job_url


class UWSRenderer(XMLRenderer):

    media_type = '*/*'

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
            self.node('uws:runId', {}, item['run_id'])
            self.node('uws:creationTime', {}, item['creation_time'])
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

        for result in data:
            self.start('uws:result', {
                'id': result['result_type'],
                'xlink:href': result['href'],
                'xlink:type': result['result_type']
            })
            self.end('uws:result')

        self.end('uws:results')

    def render_parameters(self, data, request, root=False):
        self.start('uws:parameters', self.root_attrs if root else {})

        for parameter_key, parameter_value in data.items():
            self.node('uws:parameter', {'id': parameter_key}, parameter_value)

        self.end('uws:parameters')


class UWSErrorRenderer(ErrorRenderer):

    media_type = 'application/xml'

    def render_votable(self, data, accepted_media_type=None, renderer_context=None):
        self.start('RESOURCE', {
            'type': 'results'
        })
        self.node('INFO', {
            'name': 'QUERY_STATUS',
            'value': 'ERROR'
        }, self.get_error_string(data))
        self.end('RESOURCE')
