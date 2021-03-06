from django_email_verification import send_email
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from account.models import Profile

class UserProfileSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    picture = serializers.ImageField(source="profile.picture", required=False)
    about_me = serializers.CharField(source="profile.about_me", required=False)

    class Meta:

        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'picture', 'about_me')

    def validate_email(self, value=None):

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use")
        return value

    def create(self, validated_data):

        # Removing profile fields dict from main json
        profile = {}
        if validated_data.get('picture'):
            profile['picture'] = validated_data.pop('picture')
        
        if validated_data.get('about_me'):
            profile['about_me'] = validated_data.pop('about_me')

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