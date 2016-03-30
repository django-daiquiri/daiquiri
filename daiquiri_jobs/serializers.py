from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from rest_framework import serializers

from .models import Job


class JobsSerializer(serializers.ModelSerializer):

    href = serializers.SerializerMethodField()
    phase = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ('id', 'phase', 'href')

    def get_href(self, obj):
        current_site = Site.objects.get_current()

        href = current_site.domain + reverse('uws:job-detail', args=[obj.id])

        if settings.HTTPS:
            return 'https://' + href
        else:
            return 'http://' + href

    def get_phase(self, obj):
        return obj.get_phase_str()


class JobSerializer(serializers.ModelSerializer):

    job_id = serializers.UUIDField(source='id')
    owner_id = serializers.UUIDField(source='owner.username')
    phase = serializers.SerializerMethodField()
    quote = serializers.SerializerMethodField()
    destruction = serializers.DateTimeField(source='destruction_time')

    class Meta:
        model = Job
        fields = (
            'job_id',
            'owner_id',
            'phase',
            'quote',
            'start_time',
            'end_time',
            'execution_duration',
            'destruction'
        )

    def get_phase(self, obj):
        return obj.get_phase_str()

    def get_quote(self, obj):
        return None
