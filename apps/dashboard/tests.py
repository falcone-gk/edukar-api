from account.models import Profile
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

# Create your tests here.


class TestDashboard(TestCase):
    def setUp(self) -> None:
        json_form = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "testuser",
            "last_name": "testuser",
            "password": "testpassword",
            "profile": {"about_me": "testing about me"},
        }

        # Creating user and user profile
        profile = json_form.pop("profile")
        self.user = User.objects.create_user(
            **json_form, is_staff=True, is_superuser=True
        )
        Profile.objects.create(user=self.user, **profile)

        # Getting user token
        token, _ = Token.objects.get_or_create(user=self.user)
        self.access = token.key

    def test_success_get_dashboard(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.get(
            reverse("dashboard:dashboard-info"),
        )
        print(res.content)
