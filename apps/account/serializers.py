from django.contrib.auth.models import User
from rest_framework import serializers

from account.models import Profile

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:

        model = Profile
        exclude = ('user', )

class UserProfileSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer()

    class Meta:

        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'profile')

    def create(self, validated_data):

        # Removing profile dict from main json
        profile = validated_data.pop('profile')

        user = User.objects.create_user(**validated_data)
        user.save()

        # Creating profile
        profile = Profile.objects.create(user=user, **profile)

        return user