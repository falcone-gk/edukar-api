from pyexpat import model
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from forum.models import Post, Section, Subsection

class SubsectionSerializer(serializers.ModelSerializer):

    last_post_title = serializers.SerializerMethodField()
    last_post_date = serializers.SerializerMethodField()
    last_post_author = serializers.SerializerMethodField()

    class Meta:

        model = Subsection
        fields = ('name', 'last_post_title', 'last_post_date', 'last_post_author')
    
    def get_last_post_title(self, obj):

        try:
            post_title = obj.posts.all().latest('date').title
            return post_title
        except ObjectDoesNotExist:
            return 'No post'

    def get_last_post_author(self, obj):

        try:
            post_author = obj.posts.all().latest('date').author.username
            return post_author
        except ObjectDoesNotExist:
            return 'No post'

    def get_last_post_date(self, obj):

        try:
            post_date = obj.posts.all().latest('date').get_time_difference()
            return post_date
        except ObjectDoesNotExist:
            return 'No post'

class SectionSerializer(serializers.ModelSerializer):

    subsection = SubsectionSerializer(many=True)

    class Meta:

        model = Section
        fields = ('name', 'subsection')

class PostDescriptionSerializer(serializers.ModelSerializer):

    published = serializers.CharField(source='get_time_difference')
    author = serializers.StringRelatedField()

    class Meta:

        model = Post
        fields = ('title', 'author', 'published')

class SectionWithPosts(serializers.ModelSerializer):

    posts = PostDescriptionSerializer(many=True)

    class Meta:

        model = Section
        fields = ('name', 'posts',)

class CreatePostSerializer(serializers.ModelSerializer):

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:

        model = Post
        exclude = ('date', 'slug', 'likes')

class UpdatePostSerializer(serializers.ModelSerializer):

    class Meta:

        model = Post
        fields = ('title', 'section', 'body')
