from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from forum.serializers import PostSerializer

# Create your views here.
class CreatePostAPIView(generics.CreateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer