from rest_framework.reverse import reverse

from django_user_agents.utils import get_user_agent


def get_job_url(request, kwargs):
    namespace = request.resolver_match.namespace
    base_name = request.resolver_match.url_name.rsplit('-', 1)[0]
    return reverse(f'{namespace}:{base_name}-detail', request=request, kwargs=kwargs)


def get_job_results(request, job):
    namespace = request.resolver_match.namespace
    base_name = request.resolver_match.url_name.rsplit('-', 1)[0]

    results = []
    for key in job.formats:
        url = reverse(f'{namespace}:{base_name}-result', args=[job.id, key])

        results.append({
            'result_type': key,
            'href': request.build_absolute_uri(url)
        })

    return results


def get_content_type(request, renderer):
    user_agent = get_user_agent(request)
    return 'application/xml' if user_agent.is_pc else renderer.media_type
