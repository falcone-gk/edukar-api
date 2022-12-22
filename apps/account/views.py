from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from forum.models import Post
from forum.paginators import PostCoursePagination
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
    pagination_class = PostCoursePagination
    lookup_field = 'slug'

    def get_queryset(self):

        current_user = self.request.user
        return Post.objects.filter(author=current_user).order_by('-date')