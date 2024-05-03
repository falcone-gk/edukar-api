from django.conf import settings
from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from forum.models import Post, Comment, Reply, Section
from forum.permissions import IsAuthorOrReadOnly
from core.paginators import CustomPagination
from forum.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
    ReplySerializer,
    SectionResumeSerializer,
    PostResumeSerializer,
    SectionSerializer,
    PostSerializer,
    CreatePostSerializer,
    UpdatePostSerializer,
    #CommentCreateUpdateSerializer,
    ReplyCreateSerializer,
    ReplyUpdateSerializer
)

# Create your views here.

class ForumHomeAPIView(generics.ListAPIView):

    serializer_class = SectionResumeSerializer
    queryset = Section.objects.all()

class SectionPostAPIView(generics.ListAPIView):

    serializer_class = PostResumeSerializer
    pagination_class = CustomPagination
    lookup_url_kwarg = "slug"

    def get_queryset(self):

        section = self.kwargs.get(self.lookup_url_kwarg)
        subsection = self.request.query_params.get('subsection')
        # If '0' is sent then we return all posts.
        if subsection == '0':
            return Post.objects.filter(section__slug=section).order_by('-date').order_by('-date')

        # Catch error when query param sent is not a number or empty
        try:
            queryset = Post.objects.filter(section__slug=section, subsection=int(subsection)).order_by('-date')
        except (ValueError, TypeError):
            queryset = Post.objects.filter(subsection=None).order_by('-date')
        return queryset

class SectionAPIView(generics.ListAPIView):

    serializer_class = SectionSerializer
    queryset = Section.objects.all().order_by('id')

class PostAPIView(viewsets.ModelViewSet):

    # queryset = Post.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    lookup_field = 'slug'
    pagination_class = CustomPagination

    def get_queryset(self):

        queryset = Post.objects.all()

        q = self.request.query_params.get('q')
        username = self.request.query_params.get('username')
        section = self.request.query_params.get('section')
        subsection = self.request.query_params.get('subsection')

        if q:
            queryset = queryset.filter(title__icontains=q)

        if username:
            queryset = queryset.filter(author__username=username)

        if section:
            queryset = queryset.filter(section_id=section)

        if subsection:
            queryset = queryset.filter(subsection_id=subsection)

        return queryset

    def get_throttles(self):
        if self.action == 'create' and not settings.DEBUG:
            self.throttle_scope = 'forum'
        else:
            self.throttle_scope = ''  # No throttle for other actions
        return super().get_throttles()

    def get_serializer_class(self):

        if self.action == 'create':
            return CreatePostSerializer
        elif self.action == 'retrieve' or self.action == 'list':
            return PostSerializer
        elif (self.action == 'update') | (self.action == 'partial_update'):
            return UpdatePostSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        instance_serializer = PostSerializer(instance)
        return Response(instance_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        new_instance = self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        instance_serializer = PostSerializer(new_instance)
        return Response(instance_serializer.data)

# class GetPostAPIView(generics.RetrieveAPIView):
#
#     queryset = Post.objects.all()
#     serializer_class = UpdatePostSerializer
#     lookup_field = 'slug'

class CommentAPIView(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):

    queryset = Comment.objects.all()
    #serializer_class = CommentCreateUpdateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)

    def get_serializer_class(self):

        if self.action == 'create':
            return CommentCreateSerializer
        elif (self.action == 'update') | (self.action == 'partial_update'):
            return CommentUpdateSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        instance_serializer = CommentSerializer(instance)
        return Response(instance_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        new_instance = self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        instance_serializer = CommentSerializer(new_instance)
        return Response(instance_serializer.data)
    # @staticmethod
    # def comment_serializer(request):
    #     post_id = request.data['post']
    #     comments = Comment.objects.filter(post_id=post_id)
    #     serializer = CommentSerializer(comments, many=True, context={'request': request})
    #     return serializer
    #
    # def create(self, request, *args, **kwargs):
    #     response = super().create(request, *args, **kwargs)
    #
    #     if response.status_code != 201:
    #         return response
    #
    #     serializer = self.comment_serializer(request)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    #
    # def destroy(self, request, *args, **kwargs):
    #
    #     # Check if post id was sent before deleting comment
    #     if not request.data.get('post'):
    #         msg = {'post': ['Este campo es requerido.']}
    #         return Response(msg, status=status.HTTP_400_BAD_REQUEST)
    #
    #     response = super().destroy(request, *args, **kwargs)
    #     if response.status_code != 204:
    #         return response
    #
    #     serializer = self.comment_serializer(request)
    #     # Since it has content we change status code to '200'
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    #
    # def update(self, request, *args, **kwargs):
    #     response = super().update(request, *args, **kwargs)
    #
    #     if response.status_code != 200:
    #         return response
    #
    #     serializer = self.comment_serializer(request)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

# class UnsafeCommentAPIView(viewsets.GenericViewSet):
#
#     queryset = Comment.objects.all()
#     serializer_class = CommentCreateSerializer

class ReplyAPIView(viewsets.ModelViewSet):

    queryset = Reply.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)

    def get_serializer_class(self):

        if (self.action == 'update') | (self.action == 'partial_update'):
            return ReplyUpdateSerializer
        elif self.action == 'create':
            return ReplyCreateSerializer
        else:
            return ReplySerializer

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        instance_serializer = ReplySerializer(instance)
        return Response(instance_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        new_instance = self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        instance_serializer = ReplySerializer(new_instance)
        return Response(instance_serializer.data)
