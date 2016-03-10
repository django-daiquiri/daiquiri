from django.contrib.auth.models import User

from rest_framework.serializers import ModelSerializer

from daiquiri_core.serializers import JSONField

from .models import Profile


class UserSerializer(ModelSerializer):

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
            'groups',
            'user_permissions',
        )
        read_only_fields = (
            'id',
            'last_login',
            'is_superuser',
            'username',
            'is_staff',
            'date_joined',
            'groups',
            'user_permissions'
        )


class ProfileSerializer(ModelSerializer):

    user = UserSerializer()
    details = JSONField(allow_null=True)
    attributes = JSONField(allow_null=True, read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'user', 'full_name', 'details', 'attributes')

    def update(self, obj, validated_data):
        user = validated_data.pop('user')

        # update the user for this profile seperately
        obj.user.first_name = user['first_name']
        obj.user.last_name = user['last_name']
        obj.user.email = user['email']
        obj.user.is_active = user['is_active']
        obj.user.save()

        return super(ProfileSerializer, self).update(obj, validated_data)
