from django.contrib.auth.models import Group, User

from rest_framework import serializers

from allauth.account.models import EmailAddress

from daiquiri.core.serializers import JSONDictField
from daiquiri.core.utils import get_date_display

from .models import Profile


class UserSerializer(serializers.ModelSerializer):

    date_joined_label = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'last_login',
            'is_superuser',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_active',
            'date_joined',
            'date_joined_label',
            'groups'
        )
        read_only_fields = (
            'last_login',
            'is_superuser',
            'username',
            'is_staff',
            'date_joined'
        )

    def get_date_joined_label(self, obj):
        return get_date_display(obj.date_joined)


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'name')


class EmailAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailAddress
        fields = ('email', 'verified')


class ProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    emails = serializers.SerializerMethodField(read_only=True)
    details = JSONDictField(allow_null=True)
    attributes = JSONDictField(allow_null=True)

    class Meta:
        model = Profile
        fields = (
            'id',
            'full_name',
            'user',
            'is_confirmed',
            'is_pending',
            'emails',
            'details',
            'attributes',
            'user_admin_url',
            'profile_admin_url'
        )

    def update(self, obj, validated_data):
        if 'user' in validated_data:
            user = validated_data.pop('user')

            # update the user for this profile separately
            obj.user.first_name = user['first_name']
            obj.user.last_name = user['last_name']
            obj.user.groups.set(user['groups'])
            obj.user.save()

        return super().update(obj, validated_data)

    def get_emails(self, obj):
        emails = EmailAddress.objects.filter(user=obj.user)
        serializer = EmailAddressSerializer(instance=emails, many=True)
        return serializer.data
