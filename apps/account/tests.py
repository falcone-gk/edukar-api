import json
import re
import io

from PIL import Image

from django.conf import settings
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from account.models import Profile
from forum.models import Post, Section, Subsection

# Create your tests here.

class CreateUserTests(TestCase):

    def setUp(self):

        self.json_form = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
            're_password': 'testpassword',
        }

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

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

        duplicate_user_msg = {"username":["Ya existe un usuario con este nombre."]}
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

        duplicate_user_msg = {"email":["Email ya está en uso."]}
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

        error_user_msg = {"password":["Este campo es requerido."]}
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

        error_user_msg = {"username":["Este campo es requerido."]}
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

        error_user_msg = {"email":["Este campo es requerido."]}
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

        error_user_msg = {"email":["Introduzca una dirección de correo electrónico válida."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_user_msg)

    def test_create_user_with_picture(self):

        form = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
            're_password': 'testpassword',
            'picture': self.generate_photo_file(),
            'about_me': ''
        }

        client = APIClient()
        response = client.post(
            reverse('account:user-list'),
            form,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(username='testuser')
        profile_url = user.profile.all()[0].picture.url
        self.assertEqual(profile_url, '/media/profile/test.png')

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

        error_msg = {"uid":["Este campo es requerido."],"token":["Este campo es requerido."]}
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

        error_msg = {"detail":"El token del usuario ha expirado."}
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
            reverse('account:login'), {
                'username': self.json_form['username'],
                'password': self.json_form['password']
            },
            format='json'
        )

        response_decode = response.content.decode('utf-8')
        keys_expected = ['token', 'username', 'email', 'picture']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in keys_expected:
            self.assertIn(key, response_decode)

    def test_token_auth_failed_missing_username(self):

        client = APIClient()
        response = client.post(
            reverse('account:login'), {
                'password': self.json_form['password'],
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"username":["Este campo es requerido."]})

    def test_token_auth_failed_missing_password(self):

        client = APIClient()
        response = client.post(
            reverse('account:login'), {
                'username': self.json_form['username']
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), {"password":["Este campo es requerido."]})

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

        error_msg = {"non_field_errors":["No puede iniciar sesión con las credenciales proporcionadas."]}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_msg)

    def test_login_auth_fail_no_user_active(self):

        json_form2 = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'password': 'testpassword',
            're_password': 'testpassword',
        }

        client = APIClient()
        response = client.post(
            reverse('account:user-list'),
            json_form2,
            format='json'
        )

        user = User.objects.get(username=json_form2['username'])

        self.assertFalse(user.is_active)

        client = APIClient()
        response = client.post(
            reverse('account:login'), {
                # Testing error in both field because it doesn't matter which field is wrong
                # api will give the same error.
                'username': json_form2['username'],
                'password': json_form2['password'],
            },
            format='json'
        )

        # Error happens because user is not active and cannot login
        json_res = json.loads(response.content)
        msg = {"non_field_errors":["No puede iniciar sesión con las credenciales proporcionadas."]}

        self.assertEqual(json_res, msg)

class ResetPasswordTest(TestCase):

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

        self.client = APIClient()
        self.client.post(
            reverse('account:user-reset-password'),
            {
                'email': self.json_form['email']
            }
        )

    def test_send_email_reset_password(self):

        # In 'mail.outbox' we get the email sent by Django.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.json_form['email']])
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

        # Test if email has the correct URL for activation email.
        domain = settings.DOMAIN
        reset_password_url = settings.DJOSER['PASSWORD_RESET_CONFIRM_URL'].replace('/{uid}/{token}', '')
        base_url = '{0}/{1}'.format(domain, reset_password_url)

        self.assertRegex(mail.outbox[0].body, r'{0}/(.*?)/(?P<id>[\w\.-]+)'.format(base_url))
    
    def test_reset_password_confirm_success(self):

        domain = settings.DOMAIN
        reset_password_url = settings.DJOSER['PASSWORD_RESET_CONFIRM_URL'].replace('/{uid}/{token}', '')
        base_url = '{0}/{1}'.format(domain, reset_password_url)
        search = re.search(r'{0}/(.*?)/(?P<id>[\w\.-]+)'.format(base_url), mail.outbox[0].body)
        uid, token = search.groups() # Getting the exact url generated for the frontend to activate email.

        new_password = 'test_new_password'
        self.client.post(
            reverse('account:user-reset-password-confirm'),
            {'uid': uid, 'token': token,
            'new_password': new_password, 're_new_password': new_password},
            format='json'
        )

        response = self.client.post(
            reverse('account:login'),
            {
                'username': self.json_form['username'],
                'password': new_password
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.content.decode('utf-8'))

        response = self.client.post(
            reverse('account:login'),
            {
                'username': self.json_form['username'],
                'password': 'testpassword'
            },
        )

        # Test if past password doesn't work
        error_msg = {"non_field_errors":["No puede iniciar sesión con las credenciales proporcionadas."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_msg, json.loads(response.content))
    
    def test_refresh_password_no_email_found(self):

        client = APIClient()
        response = client.post(
            reverse('account:user-reset-password'),
            {
                'email': 'wrong_email@wrong.com'
            }
        )

        error_msg = ["No existe un usuario con el email dado."]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_msg, json.loads(response.content))

class TestProfileSerializer(TestCase):

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

        # Creating user and user profile
        profile = json_form.pop('profile')
        self.user = User.objects.create_user(**json_form)
        Profile.objects.create(user=self.user, **profile)

        # Getting user token
        token, _ = Token.objects.get_or_create(user=self.user)
        self.access = token.key

    def test_get_profile_account_success(self):

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        res = client.get(reverse('account:user-me'))
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)

class BaseSetup(TestCase):
    """Setting up user, section and subsection to test post creation."""

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

        # Creating user and user profile
        profile = json_form.pop('profile')
        self.user = User.objects.create_user(**json_form)
        Profile.objects.create(user=self.user, **profile)

        json_form2 = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'first_name': 'testuser2',
            'last_name': 'testuser2',
            'password': 'testpassword',
        }

        # Creating user2
        self.user2 = User.objects.create_user(**json_form2)
        Profile.objects.create(user=self.user2, **profile)
        token, _ = Token.objects.get_or_create(user=self.user2)
        self.access2 = token.key

        # Getting user token
        token, _ = Token.objects.get_or_create(user=self.user)
        self.access = token.key

        # Creating section and subsection
        self.section = Section.objects.create(name='Cursos')
        self.subsection = Subsection.objects.create(section=self.section, name='Aritmética')

        post_form = {
            'body': '<p> test text </p>',
            'title': 'Test title'
        }

        self.num_owner_posts = 12

        for _ in range(self.num_owner_posts):
            Post.objects.create(author=self.user, section=self.section, subsection=self.subsection, **post_form)
            Post.objects.create(author=self.user2, section=self.section, subsection=self.subsection, **post_form)

class TestProfilePage(BaseSetup):

    def test_profile_home(self):

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        res = client.get(reverse('account:user-me'))
        res1 = client.get(reverse('account:user-posts-list'))

        res1_json = json.loads(res1.content)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.num_owner_posts, res1_json['count'])
        self.assertEqual(len(res1_json['results']), 5)

    def test_profile_home_error_no_user_auth(self):

        client = APIClient()
        res = client.get(reverse('account:user-me'))
        res1 = client.get(reverse('account:user-posts-list'))

        res1_json = json.loads(res1.content)
        msg = {'detail': 'Las credenciales de autenticación no se proveyeron.'}

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res1_json, msg)

    def test_delete_user_post(self):

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        post = Post.objects.filter(author=self.user)[0]
        res = client.delete(reverse('account:user-posts-detail', kwargs={'slug': post.slug}))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            # Post deleted shouldn't exist. So error must be raised
            Post.objects.get(pk=post.pk)

    def test_delete_user_post_error_no_token(self):

        client = APIClient()
        post = Post.objects.filter(author=self.user)[0]
        res = client.delete(reverse('account:user-posts-detail', kwargs={'slug': post.slug}))
        json_res = json.loads(res.content)
        msg = {"detail":"Las credenciales de autenticación no se proveyeron."}

        self.assertEqual(json_res, msg)

class TestUpdateUserInfo(BaseSetup):

    def test_update_success(self):

        info_to_update = {
            'first_name': 'new_user',
            'last_name': 'new_last_name'
        }
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        res = client.put(reverse('account:update-user'), info_to_update)

        user = User.objects.get(auth_token__key=self.access)
        current_info = {
            'first_name': user.first_name,
            'last_name': user.last_name
        }

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(info_to_update, current_info)

    def test_update_failed_no_credentials(self):

        client = APIClient()
        res = client.put(reverse('account:update-user'), {
            'first_name': 'new_user',
            'last_name': 'new_last_name'
        })

        json_res = json.loads(res.content)
        msg = {"detail":"Las credenciales de autenticación no se proveyeron."}
        self.assertEqual(json_res, msg)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_wrong_field(self):

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        res = client.put(reverse('account:update-user'), {
            'wrong_field': 'wrong'
        })

        json_res = json.loads(res.content)
        current_info = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name
        }

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Make sure info is not updated
        self.assertEqual(json_res, current_info)