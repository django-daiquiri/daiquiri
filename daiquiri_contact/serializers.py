from rest_framework import serializers

from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):

    status_label = serializers.SerializerMethodField()

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
            'message',
            'user'
        )

    def get_status_label(self, obj):
        return dict(ContactMessage.STATUS_CHOICES)[obj.status]
