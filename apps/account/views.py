from djoser.permissions import CurrentUserOrAdminOrReadOnly

from rest_framework import generics, viewsets, mixins, views, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.serializers import UpdateUserInfoSerializer, UpdateUserProfileSerializer

from forum.models import Post
from core.paginators import CustomPagination
from forum.permissions import IsAuthorOrReadOnly
from forum.serializers import PostResumeSerializer

# Create your views here.
class UserByTokenAPIView(views.APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        return Response({
            'token': user.auth_token.key,
            'username': user.username,
            'email': user.email,
            'picture': user.profile.get().picture.url,
            'has_notification': user.notif.filter(is_read=False).exists()
        })

class LogoutAPIView(views.APIView):
    def post(self, request):
        if request.user.is_authenticated:
            request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

# class UploadUserImageAPIView(APIView):
#
#     serializer_class = UploadUserImageSerializer
#     permission_classes = (IsAuthenticated,)
#
#     def post(self, request, *args, **kwargs):
#
#         context = { 'request': request }
#         serializer = UploadUserImageSerializer(data=request.data, context=context)
#         serializer.is_valid(raise_exception=True)
#         new_instance = serializer.save()
#         instance_serializer = UrlUserImageSerializer(new_instance)
#         return Response(instance_serializer.data, status=status.HTTP_201_CREATED)
