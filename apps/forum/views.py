from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from forum.models import Post, Section, Subsection
from forum.permissions import IsAuthorOrReadOnly
from forum.serializers import (
    PostSerializerResume,
    CreatePostSerializer,
    UpdatePostSerializer
)

# Create your views here.

class ForumHomeAPIView(generics.ListAPIView):

    serializer_class = PostSerializerResume
    queryset = Post.objects.all()

    def get_queryset(self):

        course = self.request.query_params.get('course')
        # If '0' is sent then we return all posts.
        if course == '0':
            return Post.objects.all()

        # Catch error when query param sent is not a number or empty
        try:
            queryset = Post.objects.filter(subsection=int(course))
        except (ValueError, TypeError):
            queryset = Post.objects.filter(subsection=None)
        return queryset

class CreateUpdatePostAPIView(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
    ):

    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly,)

    def get_serializer_class(self):

        if self.action == 'create':
            return CreatePostSerializer
        elif (self.action == 'update') | (self.action == 'partial_update'):
            return UpdatePostSerializer

    def create(self, request, *args, **kwargs):

        response = super(CreateUpdatePostAPIView, self).create(request, *args, **kwargs)

        if response.status_code == 201:
            msg = {'success': 'Post creado correctamente!'}
            return Response(msg, status=status.HTTP_201_CREATED)

        return response

    def update(self, request, *args, **kwargs):

        response = super(CreateUpdatePostAPIView, self).update(request, *args, **kwargs)

        if response.status_code == 400:
            return response

        msg = {'success': 'Post actualizado correctamente!'}
        return Response(msg, status=status.HTTP_201_CREATED)
