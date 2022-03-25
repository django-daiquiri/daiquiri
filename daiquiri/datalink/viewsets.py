from django.http import FileResponse, JsonResponse

from rest_framework import viewsets

from django_user_agents.utils import get_user_agent

from daiquiri.core.generators import generate_votable

from .constants import DATALINK_FIELDS, DATALINK_CONTENT_TYPE

from .models import Datalink


class SyncDatalinkJobViewSet(viewsets.GenericViewSet):

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

            # check for missing IDs and return error message
            for identifier in identifiers:
                if not any(filter(lambda row: row[0] == identifier, rows)):
                    rows.append((identifier, None, None, 'NotFoundFault: {}'.format(identifier), None, None, None, None))

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
