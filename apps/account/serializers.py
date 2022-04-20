from django_email_verification import send_email
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from account.models import Profile

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:

        model = Profile
        exclude = ('user', )

class UserProfileSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    profile = ProfileSerializer()

    class Meta:

        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'profile')

    def validate_email(self, value=None):

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use")
        return value

    def create(self, validated_data):

        # Removing profile dict from main json
        profile = validated_data.pop('profile')

        user = User.objects.create_user(**validated_data)
        user.is_active = False
        send_email(user)

        # Creating profile
        profile = Profile.objects.create(user=user, **profile)

        return user

class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = ('token',)