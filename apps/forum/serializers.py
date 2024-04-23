from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from forum.models import (
    Post,
    Comment,
    Reply,
    Section,
    Subsection)

class LastPostResumeSerializer(serializers.ModelSerializer):

    author = serializers.CharField(source='author.username')
    date = serializers.CharField(source='time_difference')

    class Meta:
        model = Post
        fields = ('title', 'slug', 'date', 'author')

class SubsectionResumeSerializer(serializers.ModelSerializer):

    last_post = serializers.SerializerMethodField()

    class Meta:
        model = Subsection
        fields = ('id', 'name', 'slug', 'last_post')

    def get_last_post(self, obj):

        try:
            post = obj.posts.latest('date')
            serializer = LastPostResumeSerializer(post)
            return serializer.data
        except ObjectDoesNotExist:
            return

class SectionResumeSerializer(serializers.ModelSerializer):

    subsections = SubsectionResumeSerializer(many=True, read_only=True, source='subsection')

    class Meta:
        model = Section
        fields = ('id', 'name', 'slug', 'subsections')

class AuthorSerializer(serializers.ModelSerializer):

    picture = serializers.CharField(source='profile.get.picture.url')

    class Meta:
        model = User
        fields = ('username', 'picture',)

########### Serializers for home page in forum ###########
class PostResumeSerializer(serializers.ModelSerializer):

    author = AuthorSerializer(read_only=True)
    subsection = serializers.CharField(source='subsection.name')
    num_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('title', 'slug', 'time_difference', 'author', 'subsection', 'num_comments')

    def get_num_comments(self, obj):
        return obj.comments.all().count()

########### Serializer for section and subsection ###########
class SubsectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subsection
        fields = ('id', 'name')

class SectionSerializer(serializers.ModelSerializer):

    subsections = SubsectionSerializer(many=True, read_only=True, source='subsection')

    class Meta:
        model = Section
        fields = ('id', 'name', 'slug', 'subsections')

class SectionSimplifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
        fields = ('id', 'name', 'slug')

############ Serializer about Posts ############
class CreatePostSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:

        model = Post
        read_only_fields = ('slug',)
        exclude = ('id', 'date', 'participants')
        extra_kwargs = {
            'body': {'write_only': True},
            'title': {'write_only': True},
            'section': {'write_only': True},
            'subsection': {'write_only': True},
        }

class UpdatePostSerializer(serializers.ModelSerializer):

    class Meta:

        model = Post
        fields = ('title', 'section', 'subsection', 'body',)

class ReplyCreateSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # post = serializers.IntegerField(write_only=True)

    class Meta:
        model = Reply
        fields = ('body', 'comment', 'author')
        # exclude = ('id',)
        # extra_kwargs = {
        #     'comment': {'write_only': True}
        # }

    # def create(self, validated_data):
    #     validated_data.pop('post', None)
    #     return super().create(validated_data)

class ReplyUpdateSerializer(serializers.ModelSerializer):

    # author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # post = serializers.IntegerField(write_only=True)

    class Meta:
        model = Reply
        fields = ('body',)
        # exclude = ('id', 'comment',)

    # def create(self, validated_data):
    #     validated_data.pop('post', None)
    #     return super().create(validated_data)

class CommentCreateUpdateSerializer(serializers.ModelSerializer):

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

    section = SectionSimplifiedSerializer(read_only=True)
    subsection = SubsectionSerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    date = serializers.DateTimeField(format="%d de %B del %Y, a las %H:%M")
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        exclude = ('participants',)
