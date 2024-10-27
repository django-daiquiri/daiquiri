from django.http import FileResponse, JsonResponse

from rest_framework import viewsets

from django_user_agents.utils import get_user_agent

from daiquiri.core.generators import generate_votable

from .adapter import DatalinkAdapter
from .constants import DATALINK_CONTENT_TYPE, DATALINK_FIELDS


class SyncDatalinkJobViewSet(viewsets.GenericViewSet):
    '''
    Generate the datalink VOTable
    '''

    def list(self, request):
        return self.perform_sync_job(request, request.GET)

    def create(self, request):
        return self.perform_sync_job(request, request.POST)

    def perform_sync_job(self, request, data):
        if 'ID' in data:
            identifiers = data.getlist('ID')
        else:
            identifiers = []

        adapter = DatalinkAdapter()

        # get all datalink entries (DatalinkTable, Metadata and Dynamic)
        rows = adapter.get_datalink_rows(identifiers)

        if data.get('RESPONSEFORMAT') == 'application/json':
            return JsonResponse({
                'links': [
                    {
                        'ID': row[0],
                        'access_url': row[1],
                        'service_def': row[2],
                        'error_message': row[3],
                        'description': row[4],
                        'semantics': row[5],
                        'content_type': row[6],
                        'content_length': row[7],
                    } for row in rows if not row[3]
                ]
            })
        else:
            datalink_table = generate_votable(rows, DATALINK_FIELDS)

            user_agent = get_user_agent(request)
            content_type = 'application/xml' if user_agent.is_pc else DATALINK_CONTENT_TYPE
            return FileResponse(datalink_table, content_type=content_type)
