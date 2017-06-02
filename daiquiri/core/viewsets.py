from rest_framework import mixins, viewsets

from .serializers import ChoicesSerializer


class ChoicesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ChoicesSerializer
