from rest_framework.reverse import reverse


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
