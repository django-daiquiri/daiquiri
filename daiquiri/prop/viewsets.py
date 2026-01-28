from rest_framework import viewsets
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)

from .models import Proposal
from .serializers import ProposalSerializer


class ProposalViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)

    queryset = Proposal.objects.all()

    serializer_class = ProposalSerializer

