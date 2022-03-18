from pyexpat import model
from django.contrib.auth.models import User
from rest_framework import serializers

from forum.models import Post

class PostSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:

        model = Post
        exclude = ('date', 'slug',)