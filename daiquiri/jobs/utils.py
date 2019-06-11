from rest_framework.reverse import reverse

from daiquiri.core.utils import handle_file_upload


def get_job_url(request, kwargs):
    namespace = request.resolver_match.namespace
    base_name = request.resolver_match.url_name.rsplit('-', 1)[0]
    return reverse('%s:%s-detail' % (namespace, base_name), request=request, kwargs=kwargs)


def get_job_results(request, job):
    namespace = request.resolver_match.namespace

    results = []
    for key in job.formats:
        url = reverse(namespace + ':async-result', args=[job.id, key])

        results.append({
            'result_type': key,
            'href': request.build_absolute_uri(url)
        })

    return results


def parse_upload(upload):
    resource_name, uri = upload.split(',')

    if uri.startswith('param:'):
        return {
            'resource_name': resource_name,
            'file_name': uri[len('param:'):]
        }
    else:
        return None


def handle_upload(request, data):
    if 'UPLOAD' in data:
        file_name = parse_upload(data['UPLOAD']).get('file_name')
        if file_name is not None:
            handle_file_upload(request.data[file_name], 'query', request.user)
