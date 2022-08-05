import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APIClient

from account.models import Profile

# Create your tests here.

class CreateUserTests(TestCase):

    def setUp(self):

        self.json_form = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'testuser',
            'last_name': 'testuser',
            'password': 'testpassword',
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

    def test_create_user_failed_duplicate_username(self):

        client = APIClient()

        user_form = self.json_form.copy()
        user_form['email'] = 'test2@example.com'
        client.post(
            reverse('account:create_account'),
            user_form,
            format='json'
        )

        # Testing duplicated user error message
        response = client.post(
            reverse('account:create_account'),
            self.json_form,
            format='json'
        )

        duplicate_user_msg = {"username":["A user with that username already exists."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), duplicate_user_msg)

    def test_create_user_failed_duplicate_email(self):

        client = APIClient()

        user_form = self.json_form.copy()
        user_form['username'] = 'testuser2'
        client.post(
            reverse('account:create_account'),
            user_form,
            format='json'
        )

        # Testing duplicated user error message
        response = client.post(
            reverse('account:create_account'),
            self.json_form,
            format='json'
        )

        duplicate_user_msg = {"email":["Email already in use"]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), duplicate_user_msg)

    def test_create_user_failed_no_password(self):

        user_form = self.json_form.copy()
        user_form.pop('password')

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
        user_form.pop('username')

        client = APIClient()
        response = client.post(
            reverse('account:create_account'),
            user_form,
            format='json'
        )

        error_user_msg = {"username":["This field is required."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_user_msg)

    def test_create_user_failed_no_email(self):

        user_form = self.json_form.copy()
        user_form.pop('email')

        client = APIClient()
        response = client.post(
            reverse('account:create_account'),
            user_form,
            format='json'
        )

        error_user_msg = {"email":["This field is required."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_user_msg)

    def test_create_user_failed_wrong_email_format(self):

        user_form = self.json_form.copy()
        user_form['email'] = 'wrong_email'

        client = APIClient()
        response = client.post(
            reverse('account:create_account'),
            user_form,
            format='json'
        )

        error_user_msg = {"email":["Enter a valid email address."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_user_msg)

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
            reverse('account:token_obtain_pair'), {
                'username': 'testuser',
                'password': 'testpassword',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.content.decode('utf-8'))
        self.assertIn('refresh', response.content.decode('utf-8'))

    def test_token_auth_failed_missing_username(self):

        client = APIClient()
        response = client.post(
            reverse('account:token_obtain_pair'), {
                'password': 'testpassword',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"username":["This field is required."]})

    def test_token_auth_failed_missing_passowrd(self):

        client = APIClient()
        response = client.post(
            reverse('account:token_obtain_pair'), {
                'username': 'testuser',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"password":["This field is required."]})

    def test_token_auth_failed_credential_error(self):

        client = APIClient()
        response = client.post(
            reverse('account:token_obtain_pair'), {
                # Testing error in both field because it doesn't matter which field is wrong
                # api will give the same error.
                'username': 'test_wrong_username',
                'password': 'test_wrong_password',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(json.loads(response.content), {"detail":'No active account found with the given credentials'})
