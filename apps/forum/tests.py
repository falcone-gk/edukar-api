import json

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from forum.models import Post, Section, Subsection
from account.models import Profile
# Create your tests here.

class TestSectionAndSubsection(TestCase):

    def test_signal_slug_section(self):

        name = 'Test Section'
        section = Section.objects.create(name=name)
        self.assertEqual(section.slug, slugify(name))

    def test_signal_slug_subsection(self):

        name_section = 'Test Section'
        name_subsection = 'Test Subsection'
        section = Section.objects.create(name=name_section)
        subsection = Subsection.objects.create(section=section, name=name_subsection)
        self.assertEqual(subsection.slug, slugify(name_subsection))

    def test_signal_slug_subsection_failed_no_section(self):

        name_subsection = 'Test Subsection'
        with self.assertRaises(IntegrityError):
            Subsection.objects.create(name=name_subsection)

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

        # Getting user token
        self.token, _ = Token.objects.get_or_create(user=self.user)

        # Creating section and subsection
        self.section = Section.objects.create(name='Cursos')
        self.subsection = Subsection.objects.create(section=self.section, name='Aritm??tica')

class PostCreateTestCase(BaseSetup):

    def test_create_post_success(self):

        post_form = {
            'body': '<p> test text </p>',
            'section': self.section.pk,
            'subsection': self.subsection.pk,
            'title': 'Test title'
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = client.post(
            reverse('forum:posts-list'),
            post_form,
            format='json'
        )

        msg = {'success': 'Post creado correctamente!'}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), msg)
    
    def test_create_post_missing_token(self):

        post_form = {
            'body': '<p> test text </p>',
            'section': self.section.pk,
            'subsection': self.subsection.pk,
            'title': 'Test title'
        }

        client = APIClient()
        response = client.post(
            reverse('forum:posts-list'), 
            post_form,
            format='json'
        )

        msg = {"detail":"Authentication credentials were not provided."}
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(json.loads(response.content), msg)

    def test_create_post_missing_field(self):

        post_form = {
            'body': '<p> test text </p>',
            'section': self.section.pk,
            'subsection': self.subsection.pk,
            'title': 'Test title'
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Removing body field.
        post_form.pop('body')
        response = client.post(
            reverse('forum:posts-list'), 
            post_form,
            format='json'
        )

        msg = {"body":["This field is required."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), msg)
    
    def test_title_slug_uniqueness(self):

        post_form = {
            'body': '<p> test text </p>',
            'title': 'Test title'
        }

        user = User.objects.get(username='testuser')

        Post.objects.create(author=user, section=self.section, subsection=self.subsection, **post_form)
        post2_slug = Post.objects.create(author=user, section=self.section, subsection=self.subsection, **post_form).slug
        len_posts = Post.objects.filter(slug=post2_slug).count()

        # Getting post by slug should return just one element because
        # slug is unique.
        self.assertEqual(len_posts, 1, msg="Slug field is not unique!")

class PostUpdateTestCase(BaseSetup):

    def setUp(self):
        super(PostUpdateTestCase, self).setUp()

        post_form = {
            'body': '<p> test text </p>',
            'title': 'Test title'
        }

        self.post = Post.objects.create(author=self.user, section=self.section, subsection=self.subsection, **post_form)

        # Form to use to update post created.
        self.update_form = {
            'body': '<p> test text </p>',
            'title': 'Updated title',           # <-- Field that is updated
            'section': self.section.pk,
            'subsection': self.subsection.pk,
        }

    def test_update_post_success(self):

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = client.put(
            reverse('forum:posts-detail', kwargs={'pk': self.post.pk}), 
            self.update_form,
            format='json'
        )

        new_post_title = Post.objects.get(pk=self.post.pk).title

        msg = {'success': 'Post actualizado correctamente!'}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), msg)
        self.assertEqual(new_post_title, self.update_form['title'])

    def test_update_post_missing_token(self):

        client = APIClient()
        response = client.put(
            reverse('forum:posts-detail', kwargs={'pk': self.post.pk}), 
            self.update_form,
            format='json'
        )

        msg = {"detail":"Authentication credentials were not provided."}
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(json.loads(response.content), msg)

    def test_update_post_failed_no_owner_post(self):

        json_form = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'first_name': 'testuser2',
            'last_name': 'testuser2',
            'password': 'testpassword2',
            'profile': {
                'about_me': 'testing about me'
            }
        }

        # Creating new user who will try to update post that it doesn't own.
        profile2 = json_form.pop('profile')
        user2 = User.objects.create_user(**json_form)
        Profile.objects.create(user=user2, **profile2)
        token, _ = Token.objects.get_or_create(user=user2)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = client.put(
            reverse('forum:posts-detail', kwargs={'pk': self.post.pk}), 
            self.update_form,
            format='json'
        )

        original_title = Post.objects.get(pk=self.post.pk).title

        msg = {'detail': 'You do not have permission to perform this action.'}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content), msg)
        self.assertNotEqual(original_title, self.update_form['title'])