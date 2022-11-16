from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

from forum.models import Post
from forum.paginators import PostCoursePagination
from forum.permissions import IsAuthorOrReadOnly
from forum.serializers import PostSerializerResume

from account.serializers import UserProfileSerializer, MyTokenObtainPairSerializer

# Create your views here.

class CreateUserAPIView(generics.CreateAPIView):

    serializer_class = UserProfileSerializer

    def create(self, request, *args, **kwargs):

        # Getting response to override 201 status code
        response = super(CreateUserAPIView, self).create(request, *args, **kwargs)

        # Returning the same response when error happens
        if response.status_code == 400:
            return response

        # Sending a success message instead of object (default).
        msg = {'success': 'Cuentra creada correctamente!'}
        return Response(msg, status=status.HTTP_201_CREATED)

class LoginAPIView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class OwnerPostAPIView(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):

    serializer_class = PostSerializerResume
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly,)
    pagination_class = PostCoursePagination

    def get_queryset(self):

        current_user = self.request.user
        return Post.objects.filter(author=current_user).order_by('-date')