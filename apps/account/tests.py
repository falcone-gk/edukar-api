import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

# Create your tests here.

class UserTestCase(TestCase):

    def test_create_user(self):

        json_form = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'testuser',
            'last_name': 'testuser',
            'password': 'testpassword',
            'profile': {
                'about_me': 'testing about me'
            }
        }

        client = APIClient()
        response = client.post(
            reverse('account:create_account'),
            json_form,
            format='json'
        )

        # Testing user creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Testing response content
        msg = {'success': 'Cuentra creada correctamente!'}
        self.assertEqual(json.loads(response.content), msg)

        # Testing duplicated user error message
        response = client.post(
            reverse('account:create_account'),
            json_form,
            format='json'
        )

        duplicate_user_msg = {"username":["A user with that username already exists."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), duplicate_user_msg)
    
    #def test_failed_user_creation(self):

    #    json_form = {
    #        'username': 'testuser',
    #        'email': 'testuser@example.com',
    #        'first_name': 'testuser',
    #        'last_name': 'testuser',
    #        'password': 'testpassword',
    #        'profile': {
    #            'about_me': 'testing about me'
    #        }
    #    }

    #    client = APIClient()

    #    response = client.post(
    #        reverse('account:create_account'),
    #        json_form,
    #        format='json'
    #    )

    #    json_form.pop('email')
    #    print(response.content)
    #    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
