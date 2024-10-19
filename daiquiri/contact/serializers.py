from django.template.loader import render_to_string

from rest_framework import serializers

from daiquiri.core.serializers import DateTimeLabelField

from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):

    status_label = serializers.SerializerMethodField()
    mailto = serializers.SerializerMethodField()
    created_label = DateTimeLabelField(source='created')

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

    def get_mailto(self, obj):
        return render_to_string('contact/messages_mailto.html', {
            'request': self.context.get('request'),
            'message': obj
        })
