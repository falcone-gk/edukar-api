import json
import re

from django.conf import settings
from django.core import mail
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
            'password': 'testpassword',
            're_password': 'testpassword',
        }

    def test_create_user_and_check_if_is_not_active(self):

        client = APIClient()
        response = client.post(
            reverse('account:user-list'),
            self.json_form,
            format='json'
        )

        # Testing user creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Testing response content
        msg = {'email': 'testuser@example.com', 'username': 'testuser',
                'first_name': '', 'last_name': ''}
        self.assertEqual(json.loads(response.content), msg)

        user = User.objects.get(username='testuser')
        self.assertFalse(user.is_active)

    def test_create_user_failed_duplicate_username(self):

        client = APIClient()

        user_form = self.json_form.copy()
        user_form['email'] = 'test2@example.com'
        client.post(
            reverse('account:user-list'),
            user_form,
            format='json'
        )

        # Testing duplicated user error message
        response = client.post(
            reverse('account:user-list'),
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
            reverse('account:user-list'),
            user_form,
            format='json'
        )

        # Testing duplicated user error message
        response = client.post(
            reverse('account:user-list'),
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
            reverse('account:user-list'),
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
            reverse('account:user-list'),
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
            reverse('account:user-list'),
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
            reverse('account:user-list'),
            user_form,
            format='json'
        )

        error_user_msg = {"email":["Enter a valid email address."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_user_msg)

class EmailVerificationTests(TestCase):

    def setUp(self):

        self.json_form = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
            're_password': 'testpassword',
        }

        # This POST request will send an email to the user
        self.client = APIClient()
        self.client.post(
            reverse('account:user-list'),
            self.json_form,
            format='json'
        )

    def test_user_recieved_verification_email(self):

        # In 'mail.outbox' we get the email sent by Django.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.json_form['email']])
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

        # Test if email has the correct URL for activation email.
        domain = settings.DOMAIN
        activation_url = settings.DJOSER['ACTIVATION_URL'].replace('/{uid}/{token}', '')
        base_url = '{0}/{1}'.format(domain, activation_url)

        self.assertRegex(mail.outbox[0].body, r'{0}/(.*?)/(?P<id>[\w\.-]+)'.format(base_url))

    def test_user_is_active_after_email_verification(self):

        domain = settings.DOMAIN
        activation_url = settings.DJOSER['ACTIVATION_URL'].replace('/{uid}/{token}', '')
        base_url = '{0}/{1}'.format(domain, activation_url)
        search = re.search(r'{0}/(.*?)/(?P<id>[\w\.-]+)'.format(base_url), mail.outbox[0].body)
        uid, token = search.groups() # Getting the exact url generated for the frontend to activate email.

        self.client.post(
            reverse('account:user-activation'),
            {'uid': uid, 'token': token},
            format='json'
        )

        user = User.objects.get(username=self.json_form['username'])
        self.assertTrue(user.is_active)

    def test_error_activation_email_uid_or_token_missing(self):

        response = self.client.post(
            reverse('account:user-activation'),
            format='json'
        )

        error_msg = {"uid":["This field is required."],"token":["This field is required."]}
        self.assertEqual(json.loads(response.content), error_msg)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_activation_email_when_user_already_active(self):

        domain = settings.DOMAIN
        activation_url = settings.DJOSER['ACTIVATION_URL'].replace('/{uid}/{token}', '')
        base_url = '{0}/{1}'.format(domain, activation_url)
        search = re.search(r'{0}/(.*?)/(?P<id>[\w\.-]+)'.format(base_url), mail.outbox[0].body)
        uid, token = search.groups() # Getting the exact url generated for the frontend to activate email.

        self.client.post(
            reverse('account:user-activation'),
            {'uid': uid, 'token': token},
            format='json'
        )

        # Second POST request to activate email which is wrong.
        response = self.client.post(
            reverse('account:user-activation'),
            {'uid': uid, 'token': token},
            format='json'
        )

        error_msg = {"detail":"Stale token for given user."}
        self.assertEqual(json.loads(response.content), error_msg)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TokenAuthTests(TestCase):

    def setUp(self):

        self.json_form = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'testuser',
            'last_name': 'testuser',
            'password': 'testpassword',
            'profile': {
                'about_me': 'testing about me'
            }
        }

        profile = self.json_form.pop('profile')
        user = User.objects.create_user(**self.json_form)
        Profile.objects.create(user=user, **profile)

    def test_token_auth_success(self):

        client = APIClient()
        response = client.post(
            reverse('account:jwt-create'), {
                'username': self.json_form['username'],
                'password': self.json_form['password']
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.content.decode('utf-8'))
        self.assertIn('refresh', response.content.decode('utf-8'))

    def test_token_auth_failed_missing_username(self):

        client = APIClient()
        response = client.post(
            reverse('account:jwt-create'), {
                'password': self.json_form['password'],
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"username":["This field is required."]})

    def test_token_auth_failed_missing_password(self):

        client = APIClient()
        response = client.post(
            reverse('account:jwt-create'), {
                'username': self.json_form['username']
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"password":["This field is required."]})

    def test_token_auth_failed_credential_error(self):

        client = APIClient()
        response = client.post(
            reverse('account:jwt-create'), {
                # Testing error in both field because it doesn't matter which field is wrong
                # api will give the same error.
                'username': 'test_wrong_username',
                'password': 'test_wrong_password',
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(json.loads(response.content), {"detail":'No active account found with the given credentials'})

    def test_access_token_is_working(self):

        client = APIClient()
        response = client.post(
            reverse('account:jwt-create'), {
                'username': self.json_form['username'],
                'password': self.json_form['password']
            },
            format='json'
        )

        access = json.loads(response.content)['access']

        response_verify = client.post(
            reverse('account:jwt-verify'), {
                'token': access
            },
            format='json'
        )

        self.assertEqual(response_verify.status_code, status.HTTP_200_OK)

    def test_access_token_is_wrong(self):

        client = APIClient()
        client.post(
            reverse('account:jwt-create'), {
                'username': self.json_form['username'],
                'password': self.json_form['password']
            },
            format='json'
        )

        response_verify = client.post(
            reverse('account:jwt-verify'), {
                'token': 'wrong_access_token'
            },
            format='json'
        )

        self.assertEqual(response_verify.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):

        client = APIClient()
        response = client.post(
            reverse('account:jwt-create'), {
                'username': self.json_form['username'],
                'password': self.json_form['password']
            },
            format='json'
        )
        
        refresh = json.loads(response.content)['refresh']

        response_refresh = client.post(
            reverse('account:jwt-refresh'), {
                'refresh': refresh
            },
            format='json'
        )

        self.assertIn('access', response_refresh.content.decode('utf-8'))

    def test_token_refresh_error(self):

        client = APIClient()
        refresh = 'wrong_refresh_token'

        response = client.post(
            reverse('account:jwt-refresh'), {
                'refresh': refresh
            },
            format='json'
        )

        error_msg = {"detail":"Token is invalid or expired","code":"token_not_valid"}

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(json.loads(response.content), error_msg)

