from daiquiri.query.models import QueryJob
from daiquiri.uws.viewsets import JobViewSet


class QueryJobViewSet(JobViewSet):

    detail_url_name = 'tapquery-detail'
    job_type = QueryJob.JOB_TYPE_QUERY

    def get_queryset(self):
        return QueryJob.objects.filter_by_owner(self.request.user).exclude(phase=QueryJob.PHASE_ARCHIVED)
