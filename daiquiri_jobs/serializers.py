from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from rest_framework import serializers

from .models import Job


class JobsSerializer(serializers.ModelSerializer):

    href = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ('id', 'phase', 'href')

    def get_href(self, obj):
        href = Site.objects.get_current().domain + reverse('uws:job-detail', args=[obj.id])

        if settings.HTTPS:
            return 'https://' + href
        else:
            return 'http://' + href


class JobSerializer(serializers.ModelSerializer):

    job_id = serializers.UUIDField(source='id')
    owner_id = serializers.UUIDField(source='owner.username')
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
