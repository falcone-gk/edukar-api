from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from forum.models import Post, Comment, Reply, Subsection
from forum.permissions import IsAuthorOrReadOnly
from forum.paginators import PostCoursePagination
from forum.serializers import (
    PostSerializerResume,
    SubsectionSerializer,
    PostSerializer,
    CreatePostSerializer,
    UpdatePostSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    ReplyCreateSerializer
)

# Create your views here.

def comment_serializer(request):
    post_id = request.data['post']
    comments = Comment.objects.filter(post_id=post_id)
    serializer = CommentSerializer(comments, many=True, context={'request': request})
    return serializer

class ForumHomeAPIView(generics.ListAPIView):

    serializer_class = PostSerializerResume
    pagination_class = PostCoursePagination
    queryset = Post.objects.all()

    def get_queryset(self):

        course = self.request.query_params.get('course')
        # If '0' is sent then we return all posts.
        if course == '0':
            return Post.objects.all().order_by('-date').order_by('-date')

        # Catch error when query param sent is not a number or empty
        try:
            queryset = Post.objects.filter(subsection=int(course)).order_by('-date')
        except (ValueError, TypeError):
            queryset = Post.objects.filter(subsection=None).order_by('-date')
        return queryset

class SubsectionAPIView(generics.ListAPIView):

    serializer_class = SubsectionSerializer
    queryset = Subsection.objects.all()

class CreateUpdatePostAPIView(viewsets.ModelViewSet):

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

        response = super(CreateUpdatePostAPIView, self).update(request, *args, **kwargs)

        if response.status_code == 200:
            msg = {'success': 'Post actualizado correctamente!'}
            return Response(msg, status=status.HTTP_200_OK)

        return response

class CreateUpdateCommentAPIView(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):

    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if response.status_code == 201:
            serializer = comment_serializer(request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return response

    def destroy(self, request, *args, **kwargs):

        # Check if post id was sent before deleting comment
        if not request.data.get('post'):
            msg = {'post': ['Este campo es requerido.']}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        response = super().destroy(request, *args, **kwargs)
        if response.status_code != 204:
            return response

        serializer = comment_serializer(request)
        # Since it has content we change status code to '200'
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateUpdateReplyAPIView(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):

    queryset = Reply.objects.all()
    serializer_class = ReplyCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if response.status_code == 201:
            serializer = comment_serializer(request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return response