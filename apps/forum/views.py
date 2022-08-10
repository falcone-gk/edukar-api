from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from forum.models import Post, Section, Subsection
from forum.permissions import IsAuthorOrReadOnly
from forum.serializers import SectionSerializer, SubsectionWithPosts, CreatePostSerializer, UpdatePostSerializer

# Create your views here.

class ForumHomeAPIView(generics.ListAPIView):

    serializer_class = SectionSerializer
    queryset = Section.objects.all()

class GetPostsListBySubsection(generics.RetrieveAPIView):

    queryset = Subsection.objects.all()
    serializer_class = SubsectionWithPosts
    lookup_field = 'slug'

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
