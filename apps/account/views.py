from rest_framework import generics, status
from rest_framework.response import Response

from account.serializers import UserProfileSerializer

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
