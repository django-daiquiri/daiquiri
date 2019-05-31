from django.views.generic import View

from daiquiri.core.utils import render_to_xml


class DataciteMixin(View):

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        serializer = self.serializer_class(self.object)
        renderer = self.renderer_class()

        return render_to_xml(request, renderer, serializer.data)

    def get_object(self):
        raise NotImplementedError()
