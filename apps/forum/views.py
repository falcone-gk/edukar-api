from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from forum.models import Post, Comment, Reply, Subsection
from forum.permissions import IsAuthorOrReadOnly
from forum.serializers import (
    PostSerializerResume,
    SubsectionSerializer,
    PostSerializer,
    CreatePostSerializer,
    UpdatePostSerializer,
    CommentSerializer,
    ReplySerializer
)

# Create your views here.

class ForumHomeAPIView(generics.ListAPIView):

    serializer_class = PostSerializerResume
    queryset = Post.objects.all()

    def get_queryset(self):

        course = self.request.query_params.get('course')
        # If '0' is sent then we return all posts.
        if course == '0':
            return Post.objects.all().order_by('-date')

        # Catch error when query param sent is not a number or empty
        try:
            queryset = Post.objects.filter(subsection=int(course)).order_by('-date')
        except (ValueError, TypeError):
            queryset = Post.objects.filter(subsection=None)
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

class CreateUpdateCommentAPIView(viewsets.ModelViewSet):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)

class CreateUpdateReplyAPIView(viewsets.ModelViewSet):

    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)