from django_email_verification import verify_token
from django.http import Http404, HttpResponse
from rest_framework import generics, status, views
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from account.serializers import UserProfileSerializer, TokenSerializer

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

@api_view()
def confirm(request, token):
    success, user = verify_token(token)
    if success:
        msg = {
            'success': 'Cuenta verificada',
            'username': user.username
        }
        return Response(msg)
    return Response({'error': 'Token no existe o ya ha sido usado!'})

class GetUsernameByToken(views.APIView):

    def get_object(self, token):
        try:
            return Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise Http404

    def get(self, request, token, format=None):
        token = self.get_object(token)
        return Response({'username': token.user.username}, status=status.HTTP_200_OK)
