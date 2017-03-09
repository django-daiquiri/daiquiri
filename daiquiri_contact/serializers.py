from django.contrib.auth.models import User

from rest_framework import serializers

# from allauth.account.models import EmailAddress

# from daiquiri_auth.serializers import UserSerializer, EmailAdressSerializer

from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):

    status_label = serializers.SerializerMethodField()



    class Meta:
        model = ContactMessage
        fields = '__all__'

    def get_status_label(self, obj):
        return dict(ContactMessage.STATUS_CHOICES)[obj.status]

# #    def update(self, obj, validated_data):
# #        message = validated_data.pop('message')
# #
# #        # update the user for this profile seperately
#         obj.message.author = message['author']
#         obj.message.email = message['email']
#         obj.message.subject = message['subject']
#         obj.message.id = message['id']
#         obj.message.created = message['created']
#         obj.message.message = message['message']
#         obj.message.status = message['status']
#         obj.message.save()
#
#         return super(ContactMessageSerializer, self).update(obj, validated_data)
#
#
#     def get_emails(self, obj):
#         emails = EmailAddress.objects.filter(user=obj.user)
#         serializer = EmailAddressSerializer(instance=emails, many=True)
#         return serializer.data
#
#     def get_user(self, obj):
#         user = User.objects.filter(message=obj.message)
#         serializer = UserSerializer(instance = user, many=False)