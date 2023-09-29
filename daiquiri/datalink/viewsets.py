from django.http import FileResponse, JsonResponse

from rest_framework import viewsets

from django_user_agents.utils import get_user_agent

from daiquiri.core.generators import generate_votable

from .constants import DATALINK_FIELDS, DATALINK_CONTENT_TYPE
from .adapter import DatalinkAdapter
from .models import Datalink

class SyncDatalinkJobViewSet(viewsets.GenericViewSet):
    '''Generate the datalink VOTable
    ''' 

    def list(self, request):
        return self.perform_sync_job(request, request.GET)

    def create(self, request):
        return self.perform_sync_job(request, request.POST)

    def perform_sync_job(self, request, data):

        if 'ID' in data:
            identifiers = data.getlist('ID')

        adapter = DatalinkAdapter()

        # get all datalink entries (DatalinkTable, Metadata and Dynamic)
        rows = adapter.get_datalink_rows(identifiers)

        if data.get('RESPONSEFORMAT') == 'application/json':
            return JsonResponse({
                'links': [
                    {
                        'href': row[1],
                        'text': row[4]
                    } for row in rows
                ]
            })
        else:
            datalink_table = generate_votable(rows, DATALINK_FIELDS)

            user_agent = get_user_agent(request)
            content_type = 'application/xml' if user_agent.is_pc else DATALINK_CONTENT_TYPE
            return FileResponse(datalink_table, content_type=content_type)
