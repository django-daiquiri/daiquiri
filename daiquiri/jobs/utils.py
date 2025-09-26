from django.conf import settings
from rest_framework.reverse import reverse

from django_user_agents.utils import get_user_agent


def get_job_url(request, kwargs):
    namespace = request.resolver_match.namespace
    base_name = request.resolver_match.url_name.rsplit('-', 1)[0]
    return reverse(f'{namespace}:{base_name}-detail', request=request, kwargs=kwargs)


def get_job_results(request, job):
    namespace = request.resolver_match.namespace
    base_name = request.resolver_match.url_name.rsplit('-', 1)[0]

    result_url = reverse(f'{namespace}:{base_name}-result', args=[job.id, 'result'])
    results = [{
        'result_type': 'result',
        'href': request.build_absolute_uri(result_url)
    },]
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


def get_max_records(user, max_records_settings='JOB_MAX_RECORDS'):

    max_records_config = getattr(settings, max_records_settings)

    if user is None or user.is_anonymous:
        max_records = max_records_config.get('anonymous')

    else:
        max_records = max_records_config.get('user')

        users = max_records_config.get('users')
        if users:
            user_max_records = users.get(user.username)
            max_records = user_max_records if user_max_records > max_records else max_records

        groups = max_records_config.get('groups')
        if groups:
            for group in user.groups.all():
                group_max_records = groups.get(group.name)
                max_records = group_max_records if group_max_records > max_records else max_records

    return max_records

