from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer as RestAuthLoginSerializer, UserDetailsSerializer, \
    PasswordResetSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from crowd_fund_app.forms import UserDeleteForm
from crowd_fund_app.models import CustomUser


class CustomUserDeleteSerializer(PasswordResetSerializer):
    @property
    def password_reset_form_class(self):
        return UserDeleteForm


class LoginSerializer(RestAuthLoginSerializer):
    username = None


class UserDetailsSerializer(UserDetailsSerializer):
    mobile = serializers.CharField(max_length=11)
    picture = serializers.ImageField()

    class Meta:
        extra_fields = ['username', 'email', 'first_name', 'last_name', 'mobile', 'picture', ]
        model = get_user_model()
        fields = ('pk', *extra_fields)
        read_only_fields = ('email',)


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    mobile = serializers.CharField(max_length=11)
    picture = serializers.ImageField(use_url=True, allow_empty_file=False, allow_null=False)


    # Define transaction.atomic to rollback the save operation in case of error
    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        user.first_name = self.data.get('first_name')
        user.last_name = self.data.get('last_name')
        user.mobile = self.data.get('mobile')
        user.picture = request.data.get('picture')
        user.save()
        return user


    def create(self, validated_data):
        print('creation...')
        return super().create(validated_data)


# class CustomRegisterSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(max_length=150)
#     last_name = serializers.CharField(max_length=150)
#     mobile = serializers.CharField(max_length=11)
#     picture = serializers.ImageField(use_url=True, allow_empty_file=False, allow_null=False)
#
#     class Meta:
#         model = CustomUser
#         fields = '__all__'


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'pk',
            'username',
            'first_name',
            'last_name',
            'email',
            'mobile',
            'picture',
            'birthdate',
            'facebook_profile',
        )
        read_only_fields = ('pk', 'username', 'email',)
