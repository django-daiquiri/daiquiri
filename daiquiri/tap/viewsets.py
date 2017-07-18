from rest_framework import viewsets, mixins

from daiquiri.core.responses import HttpResponseSeeOtherRedirect
from daiquiri.query.models import QueryJob
from daiquiri.query.viewsets import UWSQueryJobViewSet

from .serializers import SyncQueryJobCreateSerializer


class SyncQueryJobViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    serializer_class = SyncQueryJobCreateSerializer

    def get_queryset(self):
        return QueryJob.objects.filter_by_owner(self.request.user).exclude(phase=QueryJob.PHASE_ARCHIVED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # create the job objects
        job = self.get_queryset().model()
        job.owner = (None if self.request.user.is_anonymous() else self.request.user)
        job.table_name = serializer.data.get('TABLE_NAME')
        job.query_language = serializer.data.get('LANG')
        job.query = serializer.data.get('QUERY')

        job.clean()
        job.save()
        job.run(sync=True)

        # reload the job from the database since run doesn't work on the same job object
        return HttpResponseSeeOtherRedirect(self.get_queryset().get(pk=job.pk).result)


class AsyncQueryJobViewSet(UWSQueryJobViewSet):

    base_name = 'tap_async'
