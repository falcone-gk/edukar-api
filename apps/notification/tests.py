from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework_simplejwt.tokens import RefreshToken

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
            description='commentó en tu post'
        )

        NotificationTypes.objects.create(
            type_notif='reply',
            description='respondió a tu comentario en el post'
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

        Comment.objects.create(
            author=self.user,
            body='body comment',
            post=self.post
        )