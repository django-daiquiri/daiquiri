from django.http import FileResponse

from daiquiri.core.generators import generate_votable
from daiquiri.jobs.viewsets import SyncJobViewSet

from .constants import DATALINK_FIELDS, DATALINK_CONTENT_TYPE
from .serializers import SyncDatalinkJobSerializer
from .models import Datalink


class SyncDatalinkJobViewSet(SyncJobViewSet):
    serializer_class = SyncDatalinkJobSerializer

    parameter_map = {
        'ID': 'id',
        'RESPONSEFORMAT': 'response_format'
    }

    def perform_sync_job(self, request, data):
        rows = Datalink.objects.values_list()
        datalink_table = generate_votable(rows, DATALINK_FIELDS)
        return FileResponse(datalink_table, content_type=DATALINK_CONTENT_TYPE)
