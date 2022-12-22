import json

from django.contrib.auth.models import User
#from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
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

        # Getting user token
        token_post_owner, _ = Token.objects.get_or_create(user=self.user_post_owner)
        self.access_post_owner = token_post_owner.key

        # Creating section and subsection
        section = Section.objects.create(name='Cursos')
        subsection = Subsection.objects.create(section=section, name='Aritmética')

        # Creating default notif types
        NotificationTypes.objects.create(
            type_notif='comment',
            desc_receiver='comentó tu post',
            desc_sender='comentaste'
        )

        NotificationTypes.objects.create(
            type_notif='reply',
            desc_receiver='respondió a tu comentario',
            desc_sender='respondiste'
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
        token, _ = Token.objects.get_or_create(user=self.user)
        self.access = token.key

class TestNotificationCommentSignals(BaseNotificationTestSetup):

    def test_notification_after_comment_success(self):

        comment_form = {
            'post': self.post.pk,
            'body': '<p>Commentario</p>'
        }
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
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
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
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
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
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
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
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

class TestNotificationUsers(BaseNotificationTestSetup):

    def setUp(self):
        super().setUp()

        self.num_comments = 5
        for _ in range(self.num_comments):
            Comment.objects.create(author=self.user, body='text', post=self.post)

    def test_get_notification_received_user(self):

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access_post_owner)
        res = client.get(
            reverse('notification:notification-user-list')
        )
        json_res = json.loads(res.content)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.num_comments, json_res['count'])

    def test_deleted_notification_success(self):

        # Get notification
        notif = Notification.objects.filter(user=self.user_post_owner)[0]

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access_post_owner)
        res = client.delete(
            reverse('notification:notification-user-detail', kwargs={'pk': notif.pk})
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            Notification.objects.get(pk=notif.pk)

    def test_delete_notification_error_no_owner(self):

        # Get notification
        notif = Notification.objects.filter(user=self.user_post_owner)[0]

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        client.delete(
            reverse('notification:notification-user-detail', kwargs={'pk': notif.pk})
        )

        # Make sure that a non-owner cannot delete a notification.
        try:
            Notification.objects.get(pk=notif.pk)
        except ObjectDoesNotExist:
            self.fail('Function raised ExceptionType unexpectedly!"')

    def test_set_notifcation_as_read_success(self):

        notif = Notification.objects.filter(user=self.user_post_owner)[0]
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access_post_owner)
        res = client.post(
            reverse('notification:notification-user-set_read'),
            {'selected_notifications': [notif.pk]}
        )

        json_res = json.loads(res.content)
        self.assertTrue(json_res['has_notification'])

        notif_after_request = Notification.objects.get(pk=notif.pk)
        self.assertTrue(notif_after_request.is_read)

    def test_set_notifcation_as_read_no_identified(self):

        notif = Notification.objects.filter(user=self.user_post_owner)[0]
        client = APIClient()
        res = client.post(
            reverse('notification:notification-user-set_read'),
            {'selected_notifications': [notif.pk]}
        )

        json_res = json.loads(res.content)
        msg = {'detail': 'Las credenciales de autenticación no se proveyeron.'}
        self.assertEqual(json_res, msg)

        notif_after_request = Notification.objects.get(pk=notif.pk)
        self.assertFalse(notif_after_request.is_read)

    def test_set_notifcation_as_read_no_owner(self):

        notif = Notification.objects.filter(user=self.user_post_owner)[0]
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.access)
        res = client.post(
            reverse('notification:notification-user-set_read'),
            {'selected_notifications': [notif.pk]}
        )

        json_res = json.loads(res.content)
        msg = {'status': 'Ninguna de las notificaciones te pertenece.'}
        self.assertEqual(json_res, msg)

        notif_after_request = Notification.objects.get(pk=notif.pk)
        self.assertFalse(notif_after_request.is_read)