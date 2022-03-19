from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from forum.serializers import PostSerializer

# Create your views here.
class CreatePostAPIView(generics.CreateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer

    def post(self, request, *args, **kwargs):

        response = super(CreatePostAPIView, self).post(request, *args, **kwargs)

        if response.status_code == 400:
            return response
        
        msg = {'success': 'Post creado correctamente!'}
        return Response(msg, status=status.HTTP_201_CREATED)
