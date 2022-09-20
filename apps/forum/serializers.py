from django.contrib.auth.models import User
from rest_framework import serializers

from forum.models import (
    Post,
    Comment,
    Reply,
    Subsection)


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
        read_only_fields = ('slug',)
        exclude = ('id', 'date',)
        extra_kwargs = {
            'body': {'write_only': True},
            'title': {'write_only': True},
            'section': {'write_only': True},
            'subsection': {'write_only': True},
        }

class UpdatePostSerializer(serializers.ModelSerializer):

    class Meta:

        model = Post
        fields = ('title', 'subsection', 'body',)

class ReplyCreateSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    post = serializers.IntegerField(write_only=True)

    class Meta:
        model = Reply
        exclude = ('id',)
        extra_kwargs = {
            'comment': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data.pop('post', None)
        return super().create(validated_data)

class CommentCreateSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = '__all__'

class ReplySerializer(serializers.ModelSerializer):

    author = AuthorSerializer(read_only=True)
    date = serializers.DateTimeField(format="%d de %B del %Y, a las %H:%M", read_only=True)

    class Meta:
        model = Reply
        exclude = ('comment',)

class CommentSerializer(serializers.ModelSerializer):

    author = AuthorSerializer(read_only=True)
    date = serializers.DateTimeField(format="%d de %B del %Y, a las %H:%M", read_only=True)
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        exclude = ('post',)

class PostSerializer(serializers.ModelSerializer):

    subsection = serializers.CharField(source='subsection.name')
    author = AuthorSerializer(read_only=True)
    date = serializers.DateTimeField(format="%d de %B del %Y, a las %H:%M")
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        exclude = ('section',)