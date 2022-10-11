from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from notification.models import Notification

from notification.models import NotificationTypes
from account.models import Profile
from forum.models import Post, Comment, Reply, Section, Subsection

# Create your tests here.

class BaseNotificationTestSetup(TestCase):

    def setUp(self):

        user_form = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'testuser',
            'last_name': 'testuser',
            'password': 'testpassword',
        }

        # Creating user and user profile (the one that creates the post)
        self.user_post_owner = User.objects.create_user(**user_form)
        Profile.objects.create(user=self.user_post_owner)

        # Creating section and subsection
        section = Section.objects.create(name='Cursos')
        subsection = Subsection.objects.create(section=section, name='Aritmética')

        # Creating default notif types
        NotificationTypes.objects.create(
            type_notif='comment',
            description='comentó en tu post'
        )

        NotificationTypes.objects.create(
            type_notif='reply',
            description='respondió a tu comentario'
        )

        self.post = Post.objects.create(
            author=self.user_post_owner,
            title='Post title',
            body='post',
            section=section,
            subsection=subsection
        )

        # Creating user info that will comment or reply to comments.
        user_form2 = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'first_name': 'testuser',
            'last_name': 'testuser',
            'password': 'testpassword'
        }

        # Creating user (the one who will comment or reply)
        self.user = User.objects.create_user(**user_form2)
        Profile.objects.create(user=self.user)

        # Getting user token
        refresh = RefreshToken.for_user(self.user)
        self.access = str(refresh.access_token)

class TestNotificationCommentSignals(BaseNotificationTestSetup):

    def test_notification_after_comment_success(self):

        comment_form = {
            'post': self.post.pk,
            'body': '<p>Commentario</p>'
        }
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + self.access)
        client.post(
            reverse('forum:comments-list'),
            comment_form,
            format='json'
        )

        notif = Notification.objects.all()
        user_notif = Notification.objects.filter(user=self.user_post_owner.pk)
        self.assertEqual(len(notif), 1)
        self.assertEqual(len(user_notif), 1)

    def test_notification_no_created_after_updated_comment(self):

        comment = Comment.objects.create(author=self.user, body='text', post=self.post)
        new_text = 'updated text'
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + self.access)
        client.put(
            reverse('forum:comments-detail', kwargs={'pk': comment.pk}),
            {'post': self.post.pk, 'body': new_text},
            format='json'
        )

        # In case of the user updating their comment. This action shouldn't be notified
        notif = Notification.objects.all()
        user_notif = Notification.objects.filter(user=self.user_post_owner.pk)
        self.assertEqual(len(notif), 1)
        self.assertEqual(len(user_notif), 1)

class TestNotificationReplySignals(BaseNotificationTestSetup):

    def setUp(self):
        super().setUp()
        self.comment = Comment.objects.create(author=self.user_post_owner, body='text', post=self.post)

    def test_notification_after_reply_success(self):

        reply_form = {
            'post': self.post.pk,
            'comment': self.comment.pk,
            'body': '<p>Respuesta a comentario</p>'
        }
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + self.access)
        client.post(
            reverse('forum:replies-list'),
            reply_form,
            format='json'
        )

        notif = Notification.objects.all()
        user_notif = Notification.objects.filter(user=self.user_post_owner.pk)
        self.assertEqual(len(notif), 1)
        self.assertEqual(len(user_notif), 1)

    def test_notification_no_created_after_updated_reply(self):

        reply = Reply.objects.create(comment=self.comment, body='rand reply', author=self.user)
        new_text = 'updated text'

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + self.access)
        client.put(
            reverse('forum:replies-detail', kwargs={'pk': reply.pk}),
            {'post': self.post.pk, 'body': new_text},
            format='json'
        )

        # In case of the user updating their reply. This action shouldn't be notified
        notif = Notification.objects.all()
        user_notif = Notification.objects.filter(user=self.user_post_owner.pk)
        self.assertEqual(len(notif), 1)
        self.assertEqual(len(user_notif), 1)