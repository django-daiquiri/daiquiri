from django.template.loader import render_to_string
from django.template.defaultfilters import date

from rest_framework import serializers

from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):

    status_label = serializers.SerializerMethodField()
    mailto = serializers.SerializerMethodField()
    created_label = serializers.SerializerMethodField()

    class Meta:
        model = ContactMessage
        fields = (
            'id',
            'author',
            'email',
            'subject',
            'status',
            'status_label',
            'created',
            'created_label',
            'message',
            'user',
            'mailto'
        )

    def get_status_label(self, obj):
        return dict(ContactMessage.STATUS_CHOICES)[obj.status]

    def get_created_label(self, obj):
        return date(obj.created)

    def get_mailto(self, obj):
        return render_to_string('contact/messages_mailto.html', {
            'request': self.context.get('request'),
            'message': obj
        })
