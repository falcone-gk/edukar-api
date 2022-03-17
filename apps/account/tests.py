import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APIClient

from account.models import Profile

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

class TokenAuthTests(TestCase):

    def setUp(self):

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

        profile = json_form.pop('profile')
        user = User.objects.create_user(**json_form)
        Profile.objects.create(user=user, **profile)

    def test_token_auth_success(self):

        client = APIClient()
        response = client.post(
            reverse('account:login'), {
                'username': 'testuser',
                'password': 'testpassword',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.content.decode('utf-8'))

    def test_token_auth_failed_missing_username(self):

        client = APIClient()
        response = client.post(
            reverse('account:login'), {
                'password': 'testpassword',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"username":["This field is required."]})

    def test_token_auth_failed_missing_passowrd(self):

        client = APIClient()
        response = client.post(
            reverse('account:login'), {
                'username': 'testuser',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"password":["This field is required."]})

    def test_token_auth_failed_credential_error(self):

        client = APIClient()
        response = client.post(
            reverse('account:login'), {
                # Testing error in both field because it doesn't matter which field is wrong
                # api will give the same error.
                'username': 'test_wrong_username',
                'password': 'test_wrong_password',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"non_field_errors":["Unable to log in with provided credentials."]})