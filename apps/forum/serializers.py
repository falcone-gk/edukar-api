from dataclasses import fields
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from forum.models import Post, Section, Subsection

########### Serializers for home page in forum ###########
class PostSerializerResume(serializers.ModelSerializer):

    author = serializers.StringRelatedField()
    picture = serializers.SerializerMethodField('get_picture')

    class Meta:
        model = Post
        fields = ('title', 'slug', 'author', 'time_difference', 'picture')
    
    def get_picture(self, obj):

        request = self.context.get("request")
        return request.build_absolute_uri(obj.author.profile.get().picture.url)

########### Serializer for Course subsection ###########
class SubsectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subsection
        fields = ('id', 'name')

############ Serializer about Posts ############
class CreatePostSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:

        model = Post
        exclude = ('date', 'slug', 'likes')

class UpdatePostSerializer(serializers.ModelSerializer):

    class Meta:

        model = Post
        fields = ('title', 'section', 'body')
