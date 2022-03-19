import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from forum.models import Post
from account.models import Profile
# Create your tests here.

class PostTestCase(TestCase):

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

        self.token, _ = Token.objects.get_or_create(user=user)

    def test_create_post_success(self):

        post_form = {
            'body': '<p> test text </p>',
            'section': 'rm',
            'title': 'Test title'
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = client.post(
            reverse('forum:create_post'), 
            post_form,
            format='json'
        )

        msg = {'success': 'Post creado correctamente!'}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), msg)
    
    def test_create_post_missing_token(self):

        post_form = {
            'body': '<p> test text </p>',
            'section': 'rm',
            'title': 'Test title'
        }

        client = APIClient()
        response = client.post(
            reverse('forum:create_post'), 
            post_form,
            format='json'
        )

        msg = {"detail":"Authentication credentials were not provided."}
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(json.loads(response.content), msg)

    def test_create_post_missing_field(self):

        post_form = {
            'body': '<p> test text </p>',
            'section': 'rm',
            'title': 'Test title'
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Removing body field.
        post_form.pop('body')
        response = client.post(
            reverse('forum:create_post'), 
            post_form,
            format='json'
        )

        msg = {"body":["This field is required."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), msg)
    
    def test_title_slug_uniqueness(self):

        post_form = {
            'body': '<p> test text </p>',
            'section': 'rm',
            'title': 'Test title'
        }

        user = User.objects.get(username='testuser')

        Post.objects.create(author=user, **post_form)
        post2_slug = Post.objects.create(author=user, **post_form).slug
        len_posts = Post.objects.filter(slug=post2_slug).count()

        # Getting post by slug should return just one element because
        # slug is unique.
        self.assertEqual(len_posts, 1, msg="Slug field is not unique!")