from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from forum.models import Post, Section, Subsection

########### Serializers for home page in forum ###########
class SubsectionSerializer(serializers.ModelSerializer):

    item1 = serializers.SerializerMethodField()
    item2 = serializers.SerializerMethodField()
    item3 = serializers.SerializerMethodField()

    class Meta:

        model = Subsection
        fields = ('name', 'slug', 'item1', 'item2', 'item3')
    
    def get_item1(self, obj):
        """Returns last post title of the current subsection."""

        try:
            post_title = obj.posts.all().latest('date').title
            return post_title
        except ObjectDoesNotExist:
            return 'No post'

    def get_item2(self, obj):
        """Returns last post author of the current subsection."""

        try:
            post_author = obj.posts.all().latest('date').author.username
            return post_author
        except ObjectDoesNotExist:
            return 'No post'

    def get_item3(self, obj):
        """Returns last post date of the current subsection."""

        try:
            post_date = obj.posts.all().latest('date').get_time_difference()
            return post_date
        except ObjectDoesNotExist:
            return 'No post'

class SectionSerializer(serializers.ModelSerializer):

    subsection = SubsectionSerializer(many=True)

    class Meta:

        model = Section
        fields = ('name', 'slug', 'subsection')

############ Serializer to show subsection posts ############
class PostDescriptionSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='title')

    # Item 1 is post author username
    item1 = serializers.CharField(source='author.username')

    # Item 2 is post date
    item2 = serializers.CharField(source='get_time_difference')

    class Meta:

        model = Post
        fields = ('name', 'slug', 'item1', 'item2')

class SubsectionWithPosts(serializers.ModelSerializer):

    section = serializers.SlugRelatedField(read_only=True, slug_field='slug')
    subsection = PostDescriptionSerializer(many=True, source='posts')

    class Meta:

        model = Subsection
        fields = ('name', 'slug', 'section', 'subsection')

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
