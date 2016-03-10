from django.contrib.auth.models import User

from rest_framework.serializers import ModelSerializer, SerializerMethodField


class UserSerializer(ModelSerializer):

    details = SerializerMethodField('detail_serializer_method')

    def detail_serializer_method(self, obj):
        return obj.profile.details

    class Meta:
        model = User
        fields = (
            'id',
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
            'details'
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
