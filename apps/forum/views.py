from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from forum.models import Post, Comment, Reply, Section
from forum.permissions import IsAuthorOrReadOnly
from forum.paginators import PostCoursePagination
from forum.serializers import (
    SectionResumeSerializer,
    PostResumeSerializer,
    SectionSerializer,
    PostSerializer,
    CreatePostSerializer,
    UpdatePostSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    ReplyCreateSerializer,
    ReplyUpdateSerializer
)

# Create your views here.

class ForumHomeAPIView(generics.ListAPIView):

    serializer_class = SectionResumeSerializer
    queryset = Section.objects.all()

class SectionPostAPIView(generics.ListAPIView):

    serializer_class = PostResumeSerializer
    pagination_class = PostCoursePagination
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

class CreatePostAPIView(viewsets.ModelViewSet):

    queryset = Post.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    lookup_field = 'slug'

    def get_serializer_class(self):

        if self.action == 'create':
            return CreatePostSerializer
        elif self.action == 'retrieve':
            return PostSerializer
        elif (self.action == 'update') | (self.action == 'partial_update'):
            return UpdatePostSerializer

    def update(self, request, *args, **kwargs):

        response = super(CreatePostAPIView, self).update(request, *args, **kwargs)

        if response.status_code == 200:
            msg = {'success': 'Post actualizado correctamente!'}
            return Response(msg, status=status.HTTP_200_OK)

        return response

class GetPostAPIView(generics.RetrieveAPIView):

    queryset = Post.objects.all()
    serializer_class = UpdatePostSerializer
    lookup_field = 'slug'

class UnsafeCommentsAPI(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):

    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)

    @staticmethod
    def comment_serializer(request):
        post_id = request.data['post']
        comments = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return serializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if response.status_code != 201:
            return response

        serializer = self.comment_serializer(request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):

        # Check if post id was sent before deleting comment
        if not request.data.get('post'):
            msg = {'post': ['Este campo es requerido.']}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        response = super().destroy(request, *args, **kwargs)
        if response.status_code != 204:
            return response

        serializer = self.comment_serializer(request)
        # Since it has content we change status code to '200'
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        if response.status_code != 200:
            return response

        serializer = self.comment_serializer(request)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UnsafeCommentAPIView(UnsafeCommentsAPI):

    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer

class UnsafeReplyAPIView(UnsafeCommentsAPI):

    queryset = Reply.objects.all()
    serializer_class = ReplyCreateSerializer

    def get_serializer_class(self):

        if (self.action == 'update') | (self.action == 'partial_update'):
            return ReplyUpdateSerializer
        else:
            return ReplyCreateSerializer
