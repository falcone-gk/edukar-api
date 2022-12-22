from django.contrib.auth.models import User
from rest_framework import serializers

from account.models import Profile

class UserProfileSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    picture = serializers.ImageField(source="profile.picture", required=False)
    about_me = serializers.CharField(source="profile.about_me", required=False)

    class Meta:

        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'picture', 'about_me')

    def validate_email(self, value=None):

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email ya está en uso.")
        return value

    def create(self, validated_data):

        # Removing profile fields dict from main json
        try:
            profile = validated_data.pop('profile')
        except KeyError:
            profile = {}

        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()

        # Creating profile
        profile = Profile.objects.create(user=user, **profile)

        return user

class UserProfileInfoSerializer(serializers.ModelSerializer):

    about_me = serializers.CharField(source='profile.get.about_me')
    picture = serializers.CharField(source='profile.get.picture.url')

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 
            'username', 'email', 
            'about_me', 'picture',
        )