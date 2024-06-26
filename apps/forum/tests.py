import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from forum.models import Post, Section, Subsection, Comment, Reply
from account.models import Profile

from utils.image import generate_image
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
        token, _ = Token.objects.get_or_create(user=self.user)
        self.access = token.key

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
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.post(
            reverse('forum:posts-list'),
            post_form,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('slug', response.content.decode('utf-8'))
    
    def test_create_post_with_image_success(self):

        post_form = {
            'body': '<p> test text </p>',
            'section': self.section.pk,
            'subsection': self.subsection.pk,
            'title': 'Test title',
            'image': generate_image()
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.post(
            reverse('forum:posts-list'),
            post_form,
        )
        json_response = json.loads(response.content)
        new_post = Post.objects.get(pk=json_response['id'])

        self.assertIsNotNone(new_post.image)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
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

    # TODO: check this test for custom validation with image
    # def test_create_post_missing_field(self):
    #
    #     post_form = {
    #         'body': '<p> test text </p>',
    #         'section': self.section.pk,
    #         'subsection': self.subsection.pk,
    #         'title': 'Test title'
    #     }
    #
    #     client = APIClient()
    #     client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
    #
    #     # Removing body field.
    #     post_form.pop('body')
    #     response = client.post(
    #         reverse('forum:posts-list'), 
    #         post_form,
    #         format='json'
    #     )
    #
    #     msg = {"body":["Este campo es requerido."]}
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(json.loads(response.content), msg)
    
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

    def test_create_post_error_too_many_requests(self):

        post_form = {
            'body': '<p> test text </p>',
            'section': self.section.pk,
            'subsection': self.subsection.pk,
            'title': 'Test title'
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)

        for _ in range(3):
            response = client.post(
                reverse('forum:posts-list'),
                post_form,
                format='json'
            )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

class DeletePostTestCase(BaseSetup):

    def setUp(self):
        super(DeletePostTestCase, self).setUp()

        post_form = {
            'body': '<p> test text </p>',
            'title': 'Test title'
        }

        self.post = Post.objects.create(author=self.user, section=self.section, subsection=self.subsection, **post_form)
    
    def test_delete_post_success(self):

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.delete(reverse('forum:posts-detail', kwargs={'slug': self.post.slug}))

        with self.assertRaises(ObjectDoesNotExist):
            Post.objects.get(slug=self.post.slug)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_post_wrong_no_owner(self):

        json_form = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'first_name': 'testuser2',
            'last_name': 'testuser2',
            'password': 'testpassword',
        }
        # Creating user
        user2 = User.objects.create_user(**json_form)

        # Getting user token
        token, _ = Token.objects.get_or_create(user=user2)
        access2 = token.key

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + access2)
        response = client.delete(reverse('forum:posts-detail', kwargs={'slug': self.post.slug}))

        try:
            Post.objects.get(slug=self.post.slug)
        except ObjectDoesNotExist:
            self.fail('Ocurrió un error de manera inesperada')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class CommentsTestCase(BaseSetup):

    def setUp(self):
        super(CommentsTestCase, self).setUp()

        post_form = {
            'body': '<p> test text </p>',
            'title': 'Test title'
        }

        self.post = Post.objects.create(author=self.user, section=self.section, subsection=self.subsection, **post_form)

    def test_comment_post_success(self):

        comment_form = {
            'post': self.post.pk,
            'body': '<p>Commentario</p>'
        }
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.post(
            reverse('forum:comments-list'),
            comment_form,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_post_with_image_success(self):

        post_form = {
            'post': self.post.pk,
            'body': '<p> test text </p>',
            'image': generate_image()
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.post(
            reverse('forum:comments-list'),
            post_form,
        )
        json_response = json.loads(response.content)
        new_comment = Comment.objects.get(pk=json_response['id'])

        self.assertIsNotNone(new_comment.image)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_post_fail_missing_token(self):

        comment_form = {
            'post': self.post.pk,
            'body': '<p>Commentario</p>'
        }
        client = APIClient()
        response = client.post(
            reverse('forum:comments-list'),
            comment_form,
            format='json'
        )
        msg = {"detail":"Las credenciales de autenticación no se proveyeron."}

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(json.loads(response.content), msg)

    # TODO: check this test for custom validation with image
    # def test_comment_post_fail_missing_body(self):
    #
    #     comment_form = {
    #         'post': self.post.pk,
    #     }
    #     client = APIClient()
    #     client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
    #     response = client.post(
    #         reverse('forum:comments-list'),
    #         comment_form,
    #         format='json'
    #     )
    #     msg = {'body': ['Este campo es requerido.']}
    #
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(json.loads(response.content), msg)

    def test_delete_comment_success(self):

        # Comentario creado anteriormente para ver el retorno del delete
        Comment.objects.create(author=self.user, body='text2', post=self.post)

        comment = Comment.objects.create(author=self.user, body='text', post=self.post)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.delete(
            reverse('forum:comments-detail', kwargs={'pk': comment.pk}),
            {'post': self.post.pk},
            format='json'
        )
        num_comments = Comment.objects.filter(post=self.post).count()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Number of comments equal to '1' because of previous comment created
        self.assertEqual(num_comments, 1)

    # def test_delete_comment_failed_no_post_id(self):
    #
    #     comment = Comment.objects.create(author=self.user, body='text', post=self.post)
    #     client = APIClient()
    #     client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
    #     response = client.delete(
    #         reverse('forum:comments-detail', kwargs={'pk': comment.pk}),
    #         format='json'
    #     )
    #
    #     msg = {'post': ['Este campo es requerido.']}
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(json.loads(response.content), msg)

    def test_delete_comment_fail_no_owner(self):

        json_form = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'first_name': 'testuser2',
            'last_name': 'testuser2',
            'password': 'testpassword',
        }

        # Creating user
        user2 = User.objects.create_user(**json_form)

        # Getting user token
        token, _ = Token.objects.get_or_create(user=user2)
        access2 = token.key

        comment = Comment.objects.create(author=self.user, body='text', post=self.post)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + access2)
        response = client.delete(
            reverse('forum:comments-detail', kwargs={'pk': comment.pk}),
            {'post': self.post.pk},
            format='json'
        )

        msg = {"detail":"Usted no tiene permiso para realizar esta acción."}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content), msg)

    def test_update_comment_success(self):

        comment = Comment.objects.create(author=self.user, body='text', post=self.post)
        new_text = 'updated text'
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.patch(
            reverse('forum:comments-detail', kwargs={'pk': comment.pk}),
            {'body': new_text},
            format='json'
        )

        json_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_data['body'], new_text)

    def test_update_comment_with_image_success(self):

        comment = Comment.objects.create(author=self.user, body='text', post=self.post)
        new_image = generate_image()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.patch(
            reverse('forum:comments-detail', kwargs={'pk': comment.pk}),
            {'image': new_image},
        )

        new_comment = Comment.objects.get(pk=comment.pk)
        self.assertIsNotNone(new_comment.image)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment_fail_no_owner(self):

        json_form = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'first_name': 'testuser2',
            'last_name': 'testuser2',
            'password': 'testpassword',
        }
        # Creating user
        user2 = User.objects.create_user(**json_form)

        # Getting user token
        token, _ = Token.objects.get_or_create(user=user2)
        access2 = token.key

        comment = Comment.objects.create(author=self.user, body='text', post=self.post)
        new_text = 'updated text'

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + access2)
        response = client.put(
            reverse('forum:comments-detail', kwargs={'pk': comment.pk}),
            {'post': self.post.pk, 'body': new_text},
            format='json'
        )

        msg = {"detail":"Usted no tiene permiso para realizar esta acción."}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content), msg)
        # checking that comment is not updated
        comment_body = Comment.objects.get(id=comment.pk).body
        self.assertEqual(comment_body, comment.body)

class ReplyTestCase(BaseSetup):

    def setUp(self):
        super(ReplyTestCase, self).setUp()

        post_form = {
            'body': '<p> test text </p>',
            'title': 'Test title'
        }

        self.post = Post.objects.create(author=self.user, section=self.section, subsection=self.subsection, **post_form)
        self.comment = Comment.objects.create(author=self.user, post=self.post, body='<p> test comment </p>')

    def test_reply_comment_success(self):

        reply_form = {
            # 'post': self.post.pk,
            'comment': self.comment.pk,
            'body': '<p>Respuesta a comentario</p>'
        }
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.post(
            reverse('forum:replies-list'),
            reply_form,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reply_comment_with_image_success(self):

        reply_form = {
            'comment': self.comment.pk,
            'body': '<p>Respuesta a comentario</p>',
            'image': generate_image()
        }
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.post(
            reverse('forum:replies-list'),
            reply_form,
        )
        json_response = json.loads(response.content)
        new_reply = Reply.objects.get(pk=json_response['id'])

        self.assertIsNotNone(new_reply.image)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reply_comment_fail_missing_token(self):

        reply_form = {
            # 'post': self.post.pk,
            'comment': self.comment.pk,
            'body': '<p>Commentario</p>'
        }
        client = APIClient()
        response = client.post(
            reverse('forum:replies-list'),
            reply_form,
            format='json'
        )
        msg = {"detail":"Las credenciales de autenticación no se proveyeron."}

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(json.loads(response.content), msg)

    # TODO: check this test later
    # def test_reply_comment_fail_missing_body(self):
    #
    #     reply_form = {
    #         # 'post': self.post.pk,
    #         'comment': self.comment.pk,
    #     }
    #     client = APIClient()
    #     client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
    #     response = client.post(
    #         reverse('forum:replies-list'),
    #         reply_form,
    #         format='json'
    #     )
    #     msg = {'body': ['Este campo es requerido.']}
    #
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(json.loads(response.content), msg)

    # def test_reply_comment_fail_empty_post_id(self):
    #
    #     reply_form = {
    #         'comment': self.comment.pk,
    #         'body': '<p>Respuesta a comentario</p>'
    #     }
    #     client = APIClient()
    #     client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
    #     response = client.post(
    #         reverse('forum:replies-list'),
    #         reply_form,
    #         format='json'
    #     )
    #     msg = {"post":["Este campo es requerido."]}
    #
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(json.loads(response.content), msg)

    def test_delete_reply_success(self):

        # One reply created to check if it is maintained
        Reply.objects.create(comment=self.comment, body='rand reply2', author=self.user)
        reply = Reply.objects.create(comment=self.comment, body='rand reply', author=self.user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.delete(
            reverse('forum:replies-detail', kwargs={'pk': reply.pk}),
            {'post': self.post.pk},
            format='json'
        )
        num_replies = Reply.objects.filter(comment=self.comment).count()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Number of comments equal to '1' because of previous reply created
        self.assertEqual(num_replies, 1)

    # def test_delete_reply_failed_no_post_id(self):
    #
    #     reply = Reply.objects.create(comment=self.comment, body='rand reply', author=self.user)
    #     client = APIClient()
    #     client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
    #     response = client.delete(
    #         reverse('forum:replies-detail', kwargs={'pk': reply.pk}),
    #         format='json'
    #     )
    #
    #     msg = {'post': ['Este campo es requerido.']}
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(json.loads(response.content), msg)

    def test_delete_reply_fail_no_owner(self):

        json_form = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'first_name': 'testuser2',
            'last_name': 'testuser2',
            'password': 'testpassword',
        }

        # Creating user
        user2 = User.objects.create_user(**json_form)

        # Getting user token
        token, _ = Token.objects.get_or_create(user=user2)
        access2 = token.key

        reply = Reply.objects.create(comment=self.comment, body='rand reply', author=self.user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + access2)
        response = client.delete(
            reverse('forum:replies-detail', kwargs={'pk': reply.pk}),
            {'post': self.post.pk},
            format='json'
        )

        msg = {"detail":"Usted no tiene permiso para realizar esta acción."}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content), msg)

    def test_update_reply_success(self):

        reply = Reply.objects.create(comment=self.comment, body='rand reply', author=self.user)
        new_text = 'updated text'

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.patch(
            reverse('forum:replies-detail', kwargs={'pk': reply.pk}),
            { 'body': new_text },
            format='json'
        )

        reply_obj = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reply_obj['body'], new_text)

    def test_update_reply_with_image_success(self):

        reply = Reply.objects.create(comment=self.comment, body='rand reply', author=self.user)
        new_image = generate_image()

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        response = client.patch(
            reverse('forum:replies-detail', kwargs={'pk': reply.pk}),
            { 'image': new_image },
        )
        new_reply = Reply.objects.get(pk=reply.id)

        self.assertIsNotNone(new_reply.image)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_reply_fail_no_owner(self):

        json_form = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'first_name': 'testuser2',
            'last_name': 'testuser2',
            'password': 'testpassword',
        }
        # Creating user
        user2 = User.objects.create_user(**json_form)

        # Getting user token
        token, _ = Token.objects.get_or_create(user=user2)
        access2 = token.key
  
        reply = Reply.objects.create(comment=self.comment, body='rand reply', author=self.user)
        new_text = 'updated text'

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + access2)
        response = client.put(
            reverse('forum:replies-detail', kwargs={'pk': reply.pk}),
            {'post': self.post.pk, 'body': new_text},
            format='json'
        )

        msg = {"detail":"Usted no tiene permiso para realizar esta acción."}
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(response.content), msg)
        # checking that reply is not updated
        reply_body = Reply.objects.get(id=reply.pk).body
        self.assertEqual(reply_body, reply.body)

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
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)

        response = client.patch(
            reverse('forum:posts-detail', kwargs={'slug': self.post.slug}), 
            { 'title': 'Updated title' },
            format='json'
        )

        new_post_title = Post.objects.get(pk=self.post.pk).title

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_post_title, self.update_form['title'])

    def test_update_post_with_image_success(self):

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)

        response = client.patch(
            reverse('forum:posts-detail', kwargs={'slug': self.post.slug}), 
            { 'image': generate_image() }
        )

        new_post = Post.objects.get(pk=self.post.pk)

        self.assertIsNotNone(new_post.image)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        token, _ = Token.objects.get_or_create(user=user2)
        access = token.key

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + access)

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

        self.num_post_create = 20
        for _ in range(self.num_post_create):
            Post.objects.create(
                author=self.user,
                section=self.section,
                subsection=self.subsection,
                **self.post_form)

    def test_home_forum_api(self):
        num_new_subsections = 5
        new_subsections = ['Sub' + str(i+1) for i in range(num_new_subsections)]
        for subs in new_subsections:
            Subsection.objects.create(section=self.section, name=subs)

        client = APIClient()
        response = client.get(reverse('forum:home-forum'))
        json_res = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(json_res[0]['subsections'][0]['last_post'])

    def test_get_all_subsection(self):

        num_new_subsections = 5
        new_subsections = ['Sub' + str(i+1) for i in range(num_new_subsections)]
        for subs in new_subsections:
            Subsection.objects.create(section=self.section, name=subs)

        client = APIClient()
        response = client.get(reverse('forum:sections-list'))
        json_res = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_res[0]['subsections']), num_new_subsections + 1)

    def test_get_all_post(self):

        client = APIClient()
        url_format = '{0}?subsection={1}'
        response = client.get(
            url_format.format(reverse('forum:sections-post', kwargs={'slug': self.section.slug}),
            '0'))
        json_data = json.loads(response.content)

        self.assertEqual(json_data['count'], self.num_post_create)

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
        url_format = '{0}?subsection={1}'
        response = client.get(
            url_format.format(reverse('forum:sections-post', kwargs={'slug': self.section.slug}),
            subsection.pk))
        json_data = json.loads(response.content)
        self.assertEqual(len(json_data['results']), new_num_post_create)

    def test_no_found_subsection(self):

        client = APIClient()
        url_format = '{0}?subsection={1}'

        # Adding 'course=-1' will not found a subsection with that value
        response = client.get(
            url_format.format(reverse('forum:sections-post', kwargs={'slug': self.section.slug}),
            '-1'))
        json_data = json.loads(response.content)

        # No subsection found, we exepect an empty dictionary
        self.assertEqual(len(json_data['results']), 0)

    def test_subsection_value_is_not_number(self):

        client = APIClient()
        url_format = '{0}?subsection={1}'

        # Adding 'course=wrong_value' will trigger an error
        response = client.get(
            url_format.format(reverse('forum:sections-post', kwargs={'slug': self.section.slug}),
            'wrong_value'))
        json_data = json.loads(response.content)

        # No number value in course we expect to return an empty dictionary
        self.assertEqual(len(json_data['results']), 0)
