from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from forum.models import Post, Section, Subsection
from forum.permissions import IsAuthorOrReadOnly
from forum.serializers import SectionSerializer, SectionWithPosts, CreatePostSerializer, UpdatePostSerializer

# Create your views here.

class GetAllPostBySection(APIView):

    def get(self, request, format=None):

        sections_with_sub = Section.objects.exclude(subsection__isnull=True)
        serializer1 = SectionSerializer(sections_with_sub, many=True)

        sections_with_no_sub = Section.objects.exclude(subsection__isnull=False)
        serializer2 = SectionWithPosts(sections_with_no_sub, many=True)

        data = {
            'no_sub': serializer2.data,
            'with_sub': serializer1.data
        }

        return Response(data)

class GetPostsListBySection(generics.RetrieveAPIView):

    queryset = Section.objects.all()
    serializer_class = SectionWithPosts
    lookup_field = 'slug'

class GetPostsListBySubsection(generics.RetrieveAPIView):

    queryset = Subsection.objects.all()
    serializer_class = SectionWithPosts
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