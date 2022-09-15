import json

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

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
        refresh = RefreshToken.for_user(self.user)
        self.access = str(refresh.access_token)

        # Creating section and subsection
        self.section = Section.objects.create(name='Cursos')
        self.subsection = Subsection.objects.create(section=self.section, name='Aritmética')

class PostCreateTestCase(BaseSetup):

    def test_create_post_success(self):

        post_form = {
            'body': '<p> test text </p>',
            'section': self.section.pk,
            'subsection': self.subsection.pk,
            'title': 'Test title'
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + self.access)
        response = client.post(
            reverse('forum:posts-list'),
            post_form,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('slug', response.content.decode('utf-8'))
    
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

        msg = {"detail":"Las credenciales de autenticación no se proveyeron."}
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
        client.credentials(HTTP_AUTHORIZATION='JWT ' + self.access)

        # Removing body field.
        post_form.pop('body')
        response = client.post(
            reverse('forum:posts-list'), 
            post_form,
            format='json'
        )

        msg = {"body":["Este campo es requerido."]}
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

    def test_get_post_created_info(self):

        post_info = {
            'author': self.user,
            'body': '<p> test text </p>',
            'section': self.section,
            'subsection': self.subsection,
            'title': 'Test title'
        }
        post = Post.objects.create(**post_info)

        client = APIClient()
        response = client.get(reverse('forum:posts-detail', kwargs={'slug': post.slug}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        client.credentials(HTTP_AUTHORIZATION='JWT ' + self.access)

        response = client.put(
            reverse('forum:posts-detail', kwargs={'slug': self.post.slug}), 
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
            reverse('forum:posts-detail', kwargs={'slug': self.post.slug}),
            self.update_form,
            format='json'
        )

        msg = {"detail":"Las credenciales de autenticación no se proveyeron."}
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
        refresh = RefreshToken.for_user(user2)
        access = str(refresh.access_token)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + access)

        response = client.put(
            reverse('forum:posts-detail', kwargs={'slug': self.post.slug}), 
            self.update_form,
            format='json'
        )

        original_title = Post.objects.get(pk=self.post.pk).title

        msg = {'detail': 'Usted no tiene permiso para realizar esta acción.'}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content), msg)
        self.assertNotEqual(original_title, self.update_form['title'])

class TestForumHome(BaseSetup):

    def setUp(self):
        super(TestForumHome, self).setUp()

        self.post_form = {
            'body': '<p> test text </p>',
            'title': 'Test title'
        }

        self.num_post_create = 5
        for _ in range(self.num_post_create):
            Post.objects.create(
                author=self.user,
                section=self.section,
                subsection=self.subsection,
                **self.post_form)

    def test_get_all_subsection(self):

        num_new_subsections = 5
        new_subsections = ['Sub' + str(i+1) for i in range(num_new_subsections)]
        for subs in new_subsections:
            Subsection.objects.create(section=self.section, name=subs)

        client = APIClient()
        response = client.get(reverse('forum:subsections-list'))
        json_data = json.loads(response.content)

        # We adding one more subsection because in setup we create one by default.
        self.assertEqual(len(json_data), num_new_subsections + 1)

    def test_get_all_post(self):

        client = APIClient()
        url_format = '{0}?course={1}'
        response = client.get(url_format.format(reverse('forum:sections-list'), '0'))
        json_data = json.loads(response.content)

        self.assertEqual(len(json_data), self.num_post_create)
    
    def test_get_specific_subsection_posts(self):

        # Create new subsection
        subsection = Subsection.objects.create(section=self.section, name='Algebra')

        # Create new posts for the new subsection
        new_num_post_create = 3
        for _ in range(new_num_post_create):
            Post.objects.create(
                author=self.user,
                section=self.section,
                subsection=subsection,
                **self.post_form)

        client = APIClient()
        url_format = '{0}?course={1}'
        response = client.get(url_format.format(reverse('forum:sections-list'), subsection.pk))
        json_data = json.loads(response.content)
        self.assertEqual(len(json_data), new_num_post_create)

    def test_no_found_subsection(self):

        client = APIClient()
        url_format = '{0}?course={1}'

        # Adding 'course=-1' will not found a subsection with that value
        response = client.get(url_format.format(reverse('forum:sections-list'), '-1'))
        json_data = json.loads(response.content)

        # No subsection found, we exepect an empty dictionary
        self.assertEqual(len(json_data), 0)

    def test_subsection_value_is_not_number(self):

        client = APIClient()
        url_format = '{0}?course={1}'

        # Adding 'course=wrong_value' will trigger an error
        response = client.get(url_format.format(reverse('forum:sections-list'), 'wrong_value'))
        json_data = json.loads(response.content)

        # No number value in course we expect to return an empty dictionary
        self.assertEqual(len(json_data), 0)