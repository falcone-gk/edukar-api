from django.contrib.auth.models import User
from rest_framework import serializers

from forum.models import Post, Subsection


class AuthorSerializer(serializers.ModelSerializer):

    picture = serializers.SerializerMethodField('get_picture')

    class Meta:
        model = User
        fields = ('username', 'picture',)

    def get_picture(self, obj):

        request = self.context.get("request")
        return request.build_absolute_uri(obj.profile.get().picture.url)

########### Serializers for home page in forum ###########
class PostSerializerResume(serializers.ModelSerializer):

    author = AuthorSerializer(read_only=True)
    subsection = serializers.CharField(source='subsection.name')

    class Meta:
        model = Post
        fields = ('title', 'slug', 'time_difference', 'author', 'subsection')

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

class PostSerializer(serializers.ModelSerializer):

    subsection = serializers.CharField(source='subsection.name')
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Post
        exclude = ('id', 'likes', 'section',)