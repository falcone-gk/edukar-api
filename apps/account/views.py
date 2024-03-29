from djoser.permissions import CurrentUserOrAdminOrReadOnly

from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from account.serializers import UpdateUserInfoSerializer, UpdateUserProfileSerializer

from forum.models import Post
from core.paginators import CustomPagination
from forum.permissions import IsAuthorOrReadOnly
from forum.serializers import PostResumeSerializer

# Create your views here.

class OwnerPostAPIView(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):

    serializer_class = PostResumeSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    lookup_field = 'slug'

    def get_queryset(self):

        current_user = self.request.user
        return Post.objects.filter(author=current_user).order_by('-date')

class UpdateUserAPIView(generics.UpdateAPIView):

    serializer_class = UpdateUserInfoSerializer
    permission_classes = (CurrentUserOrAdminOrReadOnly,)

    def get_instance(self):
        return self.request.user

    def update(self, request, *args, **kwargs):

        self.get_object = self.get_instance
        return super().update(request, *args, **kwargs)

class UpdateUserProfileAPIView(generics.UpdateAPIView):

    serializer_class = UpdateUserProfileSerializer
    permission_classes = (CurrentUserOrAdminOrReadOnly,)

    def get_instance(self):
        return self.request.user.profile.get()

    def update(self, request, *args, **kwargs):

        self.get_object = self.get_instance
        response = super().update(request, *args, **kwargs)

        if response.status_code == 200:
            response.data['picture'] = request.user.profile.get().picture.url

        return response