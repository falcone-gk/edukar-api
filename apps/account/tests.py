import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from account.models import Profile

# Create your tests here.

class UserTestCase(TestCase):

    def setUp(self):

        self.json_form = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'testuser',
            'last_name': 'testuser',
            'password': 'testpassword',
            'profile': {
                # This field is not required but 'profile' field it is required
                # even though it is empty.
                'about_me': 'testing about me'
            }
        }

    def test_create_user(self):

        client = APIClient()
        response = client.post(
            reverse('account:create_account'),
            self.json_form,
            format='json'
        )

        # Testing user creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Testing response content
        msg = {'success': 'Cuentra creada correctamente!'}
        self.assertEqual(json.loads(response.content), msg)

    def test_create_user_failed_duplicate(self):

        user_form = self.json_form.copy()
        profile = user_form.pop('profile')
        user = User.objects.create_user(**user_form)
        Profile.objects.create(user=user, **profile)

        # Testing duplicated user error message
        client = APIClient()
        response = client.post(
            reverse('account:create_account'),
            self.json_form,
            format='json'
        )

        duplicate_user_msg = {"username":["A user with that username already exists."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), duplicate_user_msg)

    def test_create_user_failed_no_password(self):

        user_form = self.json_form.copy()
        user_form.pop('password', None)

        client = APIClient()
        response = client.post(
            reverse('account:create_account'),
            user_form,
            format='json'
        )

        error_user_msg = {"password":["This field is required."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_user_msg)

    def test_create_user_failed_no_username(self):

        user_form = self.json_form.copy()
        user_form.pop('username', None)

        client = APIClient()
        response = client.post(
            reverse('account:create_account'),
            user_form,
            format='json'
        )

        error_user_msg = {"username":["This field is required."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_user_msg)
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

class UserTestsWithToken(TestCase):

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
        self.user = User.objects.create_user(**json_form)
        Profile.objects.create(user=self.user, **profile)
        self.token, _ = Token.objects.get_or_create(user=self.user)

    def test_get_username_by_token(self):

        client = APIClient()
        response = client.get(reverse('account:get-username', kwargs={'token': self.token.key}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), {"username": "testuser"})

    def test_get_username_by_token_failed(self):

        client = APIClient()
        response = client.get(reverse('account:get-username', kwargs={'token': 'wrong_token'}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content), {"detail": "Not found."})