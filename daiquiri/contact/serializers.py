from urllib.parse import quote

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
        subject = f"Re: {obj.subject}"

        body = (
            "\n\n"
            f"On {obj.created.strftime('%Y-%m-%d %H:%M')} {obj.author} wrote:\n"
            f"> {obj.message}"
        )

        return (
            f"mailto:{obj.email}"
            f"?subject={quote(subject)}"
            f"&body={quote(body)}"
        )