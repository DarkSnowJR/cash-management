import authentication.serializers
from rest_framework import serializers, exceptions
from . import models
from django.contrib import auth
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'
    }

    class Meta:
        model = models.User
        fields = ['username', 'password', ]

    def validate(self, attrs):
        username = attrs.get('username', '')
        if not username.isalnum():
            raise serializers.ValidationError(self.default_error_messages)

        return attrs

    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    """
    Serializer for user login
    """
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = models.User.objects.get(username=obj['username'])
        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = models.User
        fields = ['password', 'username', 'tokens']

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if not user:
            raise exceptions.AuthenticationFailed('Invalid credentials, try again')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('Account disabled, contact admin')

        return {
            'username': user.username,
            'tokens': user.tokens
        }


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for user logout
    """
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': 'Token is expired or invalid'
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user
    """

    class Meta:
        model = models.User
        fields = ('pk', 'username', )
