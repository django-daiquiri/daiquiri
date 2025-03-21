from django.template.loader import render_to_string

from rest_framework import serializers

from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):

    mailto = serializers.SerializerMethodField()

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

    def get_mailto(self, obj):
        return render_to_string('contact/messages_mailto.html', {
            'request': self.context.get('request'),
            'message': obj
        })
