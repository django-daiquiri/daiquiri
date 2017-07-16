from daiquiri.jobs.models import Job
from daiquiri.uws.viewsets import JobsViewSet


class QueryJobsViewSet(JobsViewSet):
    detail_url_name = 'tapquery-detail'
    job_type = Job.JOB_TYPE_QUERY
