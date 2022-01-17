from django.http import FileResponse

from daiquiri.core.generators import generate_votable
from daiquiri.jobs.viewsets import SyncJobViewSet

from .constants import DATALINK_FIELDS, DATALINK_CONTENT_TYPE

from .models import Datalink


class SyncDatalinkJobViewSet(SyncJobViewSet):

    def list(self, request):
        return self.perform_sync_job(request, request.GET)

    def create(self, request):
        return self.perform_sync_job(request, request.POST)

    def perform_sync_job(self, request, data):
        rows = []

        if 'ID' in data:
            identifiers = data.getlist('ID')
            field_names = [field['name'] for field in DATALINK_FIELDS]
            rows = list(Datalink.objects.filter(ID__in=identifiers).values_list(*field_names))

            # check for missing IDs
            for identifier in identifiers:
                if not any(filter(lambda row: row[0] == identifier, rows)):
                    rows.append((identifier, None, None, 'Not found: {}'.format(identifier), None, None, None, None))

        datalink_table = generate_votable(rows, DATALINK_FIELDS)
        return FileResponse(datalink_table, content_type=DATALINK_CONTENT_TYPE)
