from urllib.parse import quote

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
        subject = f"Re: {obj.subject or ''}"

        created = (
            obj.created.strftime('%Y-%m-%d %H:%M')
            if obj.created
            else ''
        )

        author = obj.author or 'Unknown'
        message = obj.message or ''

        body = (
            "\n\n"
            f"On {created} {author} wrote:\n"
            f"> {message}"
        )

        return (
            f"mailto:{obj.email}"
            f"?subject={quote(subject)}"
            f"&body={quote(body)}"
        )