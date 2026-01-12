import io
import json
import re
from decimal import Decimal

from account.models import Profile, UserProduct
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from forum.models import Post, Section, Subsection
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from store.models import Category, Product, Sell

from helpers.choices import SellStatus

# Create your tests here.


class CreateUserTests(TestCase):
    def setUp(self):
        self.json_form = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "re_password": "testpassword",
        }

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        return file

    def test_create_user_and_check_if_is_not_active(self):
        client = APIClient()
        response = client.post(
            reverse("account:user-list"), self.json_form, format="json"
        )

        # Testing user creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Testing response content
        msg = {
            "email": "testuser@example.com",
            "username": "testuser",
            "first_name": "",
            "last_name": "",
        }
        self.assertEqual(json.loads(response.content), msg)

        user = User.objects.get(username="testuser")
        self.assertFalse(user.is_active)

    def test_create_user_failed_duplicate_username(self):
        client = APIClient()

        user_form = self.json_form.copy()
        user_form["email"] = "test2@example.com"
        client.post(reverse("account:user-list"), user_form, format="json")

        # Testing duplicated user error message
        response = client.post(
            reverse("account:user-list"), self.json_form, format="json"
        )

        duplicate_user_msg = {
            "username": ["Ya existe un usuario con este nombre."]
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), duplicate_user_msg)

    def test_create_user_failed_duplicate_email(self):
        client = APIClient()

        user_form = self.json_form.copy()
        user_form["username"] = "testuser2"
        client.post(reverse("account:user-list"), user_form, format="json")

        # Testing duplicated user error message
        response = client.post(
            reverse("account:user-list"), self.json_form, format="json"
        )

        duplicate_user_msg = {"email": ["Email ya está en uso."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), duplicate_user_msg)

    def test_create_user_failed_no_password(self):
        user_form = self.json_form.copy()
        user_form.pop("password")

        client = APIClient()
        response = client.post(
            reverse("account:user-list"), user_form, format="json"
        )

        error_user_msg = {"password": ["Este campo es requerido."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_user_msg)

    def test_create_user_failed_no_username(self):
        user_form = self.json_form.copy()
        user_form.pop("username")

        client = APIClient()
        response = client.post(
            reverse("account:user-list"), user_form, format="json"
        )

        error_user_msg = {"username": ["Este campo es requerido."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_user_msg)

    def test_create_user_failed_no_email(self):
        user_form = self.json_form.copy()
        user_form.pop("email")

        client = APIClient()
        response = client.post(
            reverse("account:user-list"), user_form, format="json"
        )

        error_user_msg = {"email": ["Este campo es requerido."]}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_user_msg)

    def test_create_user_failed_wrong_email_format(self):
        user_form = self.json_form.copy()
        user_form["email"] = "wrong_email"

        client = APIClient()
        response = client.post(
            reverse("account:user-list"), user_form, format="json"
        )

        error_user_msg = {
            "email": ["Introduzca una dirección de correo electrónico válida."]
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_user_msg)

    def test_create_user_with_picture(self):
        form = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "re_password": "testpassword",
            "picture": self.generate_photo_file(),
            "about_me": "",
        }

        client = APIClient()
        response = client.post(
            reverse("account:user-list"),
            form,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="testuser")
        profile_url = user.profile.all()[0].picture.url
        self.assertEqual(profile_url, "/media/profile/testuser.png")


class EmailVerificationTests(TestCase):
    def setUp(self):
        self.json_form = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
            "re_password": "testpassword",
        }

        # This POST request will send an email to the user
        self.client = APIClient()
        self.client.post(
            reverse("account:user-list"), self.json_form, format="json"
        )

    def test_user_recieved_verification_email(self):
        # In 'mail.outbox' we get the email sent by Django.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.json_form["email"]])
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

        # Test if email has the correct URL for activation email.
        domain = settings.DOMAIN
        activation_url = settings.DJOSER["ACTIVATION_URL"].replace(
            "/{uid}/{token}", ""
        )
        base_url = "{0}/{1}".format(domain, activation_url)

        self.assertRegex(
            mail.outbox[0].body, r"{0}/(.*?)/(?P<id>[\w\.-]+)".format(base_url)
        )

    def test_user_is_active_after_email_verification(self):
        domain = settings.DOMAIN
        activation_url = settings.DJOSER["ACTIVATION_URL"].replace(
            "/{uid}/{token}", ""
        )
        base_url = "{0}/{1}".format(domain, activation_url)
        search = re.search(
            r"{0}/(.*?)/(?P<id>[\w\.-]+)".format(base_url), mail.outbox[0].body
        )
        uid, token = (
            search.groups()
        )  # Getting the exact url generated for the frontend to activate email.

        self.client.post(
            reverse("account:user-activation"),
            {"uid": uid, "token": token},
            format="json",
        )

        user = User.objects.get(username=self.json_form["username"])
        self.assertTrue(user.is_active)

    def test_error_activation_email_uid_or_token_missing(self):
        response = self.client.post(
            reverse("account:user-activation"), format="json"
        )

        error_msg = {
            "uid": ["Este campo es requerido."],
            "token": ["Este campo es requerido."],
        }
        self.assertEqual(json.loads(response.content), error_msg)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_activation_email_when_user_already_active(self):
        domain = settings.DOMAIN
        activation_url = settings.DJOSER["ACTIVATION_URL"].replace(
            "/{uid}/{token}", ""
        )
        base_url = "{0}/{1}".format(domain, activation_url)
        search = re.search(
            r"{0}/(.*?)/(?P<id>[\w\.-]+)".format(base_url), mail.outbox[0].body
        )
        uid, token = (
            search.groups()
        )  # Getting the exact url generated for the frontend to activate email.

        self.client.post(
            reverse("account:user-activation"),
            {"uid": uid, "token": token},
            format="json",
        )

        # Second POST request to activate email which is wrong.
        response = self.client.post(
            reverse("account:user-activation"),
            {"uid": uid, "token": token},
            format="json",
        )

        error_msg = {"detail": "El token del usuario ha expirado."}
        self.assertEqual(json.loads(response.content), error_msg)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TokenAuthTests(TestCase):
    def setUp(self):
        self.json_form = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "testuser",
            "last_name": "testuser",
            "password": "testpassword",
            "profile": {"about_me": "testing about me"},
        }

        profile = self.json_form.pop("profile")
        self.user = User.objects.create_user(**self.json_form)
        Profile.objects.create(user=self.user, **profile)

    def test_token_auth_success(self):
        client = APIClient()
        response = client.post(
            reverse("account:login"),
            {
                "username": self.json_form["username"],
                "password": self.json_form["password"],
            },
            format="json",
        )

        response_decode = response.content.decode("utf-8")
        keys_expected = ["token", "username", "email", "picture"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in keys_expected:
            self.assertIn(key, response_decode)

    def test_token_auth_failed_missing_username(self):
        client = APIClient()
        response = client.post(
            reverse("account:login"),
            {
                "password": self.json_form["password"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content),
            {"username": ["Este campo es requerido."]},
        )

    def test_token_auth_failed_missing_password(self):
        client = APIClient()
        response = client.post(
            reverse("account:login"),
            {"username": self.json_form["username"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content),
            {"password": ["Este campo es requerido."]},
        )

    def test_token_auth_failed_credential_error(self):
        client = APIClient()
        response = client.post(
            reverse("account:login"),
            {
                # Testing error in both field because it doesn't matter which field is wrong
                # api will give the same error.
                "username": "test_wrong_username",
                "password": "test_wrong_password",
            },
            format="json",
        )

        error_msg = {
            "non_field_errors": [
                "No puede iniciar sesión con las credenciales proporcionadas."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content), error_msg)

    def test_login_auth_fail_no_user_active(self):
        json_form2 = {
            "username": "testuser2",
            "email": "testuser2@example.com",
            "password": "testpassword",
            "re_password": "testpassword",
        }

        client = APIClient()
        response = client.post(
            reverse("account:user-list"), json_form2, format="json"
        )

        user = User.objects.get(username=json_form2["username"])

        self.assertFalse(user.is_active)

        client = APIClient()
        response = client.post(
            reverse("account:login"),
            {
                # Testing error in both field because it doesn't matter which field is wrong
                # api will give the same error.
                "username": json_form2["username"],
                "password": json_form2["password"],
            },
            format="json",
        )

        # Error happens because user is not active and cannot login
        json_res = json.loads(response.content)
        msg = {
            "non_field_errors": [
                "No puede iniciar sesión con las credenciales proporcionadas."
            ]
        }

        self.assertEqual(json_res, msg)

    def test_get_user_by_token(self):
        client = APIClient()
        token, _ = Token.objects.get_or_create(user=self.user)
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = client.post(reverse("account:user-data"))
        json_data = json.loads(response.content)

        keys_expected = [
            "token",
            "username",
            "email",
            "picture",
            "has_notification",
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in keys_expected:
            self.assertIn(key, json_data)

    def test_get_user_by_token_fail_no_auth(self):
        client = APIClient()
        response = client.post(reverse("account:user-data"))
        json_data = json.loads(response.content)
        error_msg = {
            "detail": "Las credenciales de autenticación no se proveyeron."
        }

        self.assertEqual(json_data, error_msg)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_by_token_fail_wrong_token(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + "wrong_token")
        response = client.post(reverse("account:user-data"))
        json_data = json.loads(response.content)
        error_msg = {"detail": "Token inválido."}

        self.assertEqual(json_data, error_msg)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        # First login with credentials
        client = APIClient()
        token, _ = Token.objects.get_or_create(user=self.user)
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = client.post(reverse("account:logout"))
        has_token = Token.objects.filter(user=self.user).exists()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(has_token)


class ResetPasswordTest(TestCase):
    def setUp(self):
        self.json_form = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "testuser",
            "last_name": "testuser",
            "password": "testpassword",
            "profile": {"about_me": "testing about me"},
        }

        profile = self.json_form.pop("profile")
        user = User.objects.create_user(**self.json_form)
        Profile.objects.create(user=user, **profile)

        self.client = APIClient()
        self.client.post(
            reverse("account:user-reset-password"),
            {"email": self.json_form["email"]},
        )

    def test_send_email_reset_password(self):
        # In 'mail.outbox' we get the email sent by Django.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.json_form["email"]])
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

        # Test if email has the correct URL for activation email.
        domain = settings.DOMAIN
        reset_password_url = settings.DJOSER[
            "PASSWORD_RESET_CONFIRM_URL"
        ].replace("/{uid}/{token}", "")
        base_url = "{0}/{1}".format(domain, reset_password_url)

        self.assertRegex(
            mail.outbox[0].body, r"{0}/(.*?)/(?P<id>[\w\.-]+)".format(base_url)
        )

    def test_reset_password_confirm_success(self):
        domain = settings.DOMAIN
        reset_password_url = settings.DJOSER[
            "PASSWORD_RESET_CONFIRM_URL"
        ].replace("/{uid}/{token}", "")
        base_url = "{0}/{1}".format(domain, reset_password_url)
        search = re.search(
            r"{0}/(.*?)/(?P<id>[\w\.-]+)".format(base_url), mail.outbox[0].body
        )
        uid, token = (
            search.groups()
        )  # Getting the exact url generated for the frontend to activate email.

        new_password = "test_new_password"
        self.client.post(
            reverse("account:user-reset-password-confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": new_password,
                "re_new_password": new_password,
            },
            format="json",
        )

        response = self.client.post(
            reverse("account:login"),
            {"username": self.json_form["username"], "password": new_password},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.content.decode("utf-8"))

        response = self.client.post(
            reverse("account:login"),
            {
                "username": self.json_form["username"],
                "password": "testpassword",
            },
        )

        # Test if past password doesn't work
        error_msg = {
            "non_field_errors": [
                "No puede iniciar sesión con las credenciales proporcionadas."
            ]
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_msg, json.loads(response.content))

    def test_refresh_password_no_email_found(self):
        client = APIClient()
        response = client.post(
            reverse("account:user-reset-password"),
            {"email": "wrong_email@wrong.com"},
        )

        error_msg = ["No existe un usuario con el email dado."]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_msg, json.loads(response.content))


class TestProfileSerializer(TestCase):
    def setUp(self):
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
        self.user = User.objects.create_user(**json_form)
        Profile.objects.create(user=self.user, **profile)

        # Getting user token
        token, _ = Token.objects.get_or_create(user=self.user)
        self.access = token.key

    def test_get_profile_account_success(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.get(reverse("account:user-me"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class BaseSetup(TestCase):
    """Setting up user, section and subsection to test post creation."""

    def setUp(self):
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
        self.user = User.objects.create_user(**json_form)
        Profile.objects.create(user=self.user, **profile)

        json_form2 = {
            "username": "testuser2",
            "email": "testuser2@example.com",
            "first_name": "testuser2",
            "last_name": "testuser2",
            "password": "testpassword",
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
        self.section = Section.objects.create(name="Cursos")
        self.subsection = Subsection.objects.create(
            section=self.section, name="Aritmética"
        )

        post_form = {"body": "<p> test text </p>", "title": "Test title"}

        self.num_owner_posts = 12

        for _ in range(self.num_owner_posts):
            Post.objects.create(
                author=self.user,
                section=self.section,
                subsection=self.subsection,
                **post_form,
            )
            Post.objects.create(
                author=self.user2,
                section=self.section,
                subsection=self.subsection,
                **post_form,
            )


class TestProfilePage(BaseSetup):
    def test_profile_home(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.get(reverse("account:user-me"))
        res1 = client.get(reverse("account:user-posts-list"))

        res1_json = json.loads(res1.content)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.num_owner_posts, res1_json["count"])
        self.assertEqual(len(res1_json["results"]), 5)

    def test_profile_home_error_no_user_auth(self):
        client = APIClient()
        res = client.get(reverse("account:user-me"))
        res1 = client.get(reverse("account:user-posts-list"))

        res1_json = json.loads(res1.content)
        msg = {"detail": "Las credenciales de autenticación no se proveyeron."}

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res1_json, msg)

    def test_delete_user_post(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        post = Post.objects.filter(author=self.user)[0]
        res = client.delete(
            reverse("account:user-posts-detail", kwargs={"slug": post.slug})
        )

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            # Post deleted shouldn't exist. So error must be raised
            Post.objects.get(pk=post.pk)

    def test_delete_user_post_error_no_token(self):
        client = APIClient()
        post = Post.objects.filter(author=self.user)[0]
        res = client.delete(
            reverse("account:user-posts-detail", kwargs={"slug": post.slug})
        )
        json_res = json.loads(res.content)
        msg = {"detail": "Las credenciales de autenticación no se proveyeron."}

        self.assertEqual(json_res, msg)


class TestUpdateUserInfo(BaseSetup):
    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        return file

    def test_update_success(self):
        info_to_update = {
            "first_name": "new_user",
            "last_name": "new_last_name",
        }
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        # res = client.patch(reverse('account:update-user'), info_to_update)
        res = client.patch(reverse("account:user-me"), info_to_update)

        user = User.objects.get(auth_token__key=self.access)
        current_info = {
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(info_to_update, current_info)

    def test_update_one_field_success(self):
        info_to_update = {
            "first_name": "new_user",
        }
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.patch(reverse("account:user-me"), info_to_update)

        user = User.objects.get(auth_token__key=self.access)
        current_info = {
            "first_name": user.first_name,
        }

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(info_to_update, current_info)

    def test_update_failed_no_credentials(self):
        client = APIClient()
        res = client.patch(
            reverse("account:user-me"),
            {"first_name": "new_user", "last_name": "new_last_name"},
        )

        json_res = json.loads(res.content)
        msg = {"detail": "Las credenciales de autenticación no se proveyeron."}
        self.assertEqual(json_res, msg)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_wrong_field(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.patch(reverse("account:user-me"), {"wrong_field": "wrong"})

        json_res = json.loads(res.content)
        current_info = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "testuser",
            "last_name": "testuser",
            "about_me": "testing about me",
            "picture": "http://testserver/media/default-avatar.jpg",
        }

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Make sure info is not updated
        self.assertEqual(json_res, current_info)

    def test_update_username_success(self):
        new_username = "new_testuser"

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.patch(
            reverse("account:user-me"), {"username": new_username}
        )

        json_res = json.loads(res.content)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Make sure info is not updated
        self.assertEqual(json_res["username"], new_username)

    def test_update_email_error(self):
        new_email = "new_email@test.com"

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.patch(reverse("account:user-me"), {"email": new_email})

        json_res = json.loads(res.content)

        # We don't test status because request will return HTPP 200
        # self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Make sure info is not updated
        self.assertNotEqual(json_res["email"], new_email)

    def test_update_username_error_name_already_used(self):
        new_username = "testuser2"

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.patch(
            reverse("account:user-me"), {"username": new_username}
        )

        json_res = json.loads(res.content)
        msg = {"username": ["Ya existe un usuario con este nombre."]}

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json_res, msg)

    def test_update_username_error_empty_field(self):
        new_username = ""

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.patch(
            reverse("account:user-me"), {"username": new_username}
        )

        json_res = json.loads(res.content)
        msg = {"username": ["Este campo no puede estar en blanco."]}

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json_res, msg)

    def test_update_profile_success(self):
        info_to_update = {
            "about_me": "new_about_me",
            "picture": self.generate_photo_file(),
        }

        old_info = {
            "about_me": self.user.profile.get().about_me,
            "picture": self.user.profile.get().picture.name,
        }

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.patch(reverse("account:user-me"), info_to_update)

        user = Profile.objects.get(user=self.user.pk)
        current_info = {"about_me": user.about_me, "picture": user.picture.name}

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(old_info, current_info)

    def test_update_profile_error_no_credentials(self):
        info_to_update = {
            "about_me": "new_about_me",
            "picture": self.generate_photo_file(),
        }

        client = APIClient()
        res = client.put(reverse("account:user-me"), info_to_update)

        json_res = json.loads(res.content)
        msg = {"detail": "Las credenciales de autenticación no se proveyeron."}

        self.assertEqual(json_res, msg)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUserProductsView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_active=True,
        )
        self.solution_category = Category.objects.create(
            name="Solucionario", is_one_time_purchase=False
        )
        self.other_category = Category.objects.create(
            name="Otros", is_one_time_purchase=True
        )

        # Create products
        self.product1 = Product.objects.create(
            name="Solucionario Matemáticas",
            price=Decimal("29.99"),
            category=self.solution_category,
        )
        self.product2 = Product.objects.create(
            name="Solucionario Física",
            price=Decimal("34.99"),
            category=self.solution_category,
        )
        self.other_product = Product.objects.create(
            name="Otro Producto",
            price=Decimal("19.99"),
            category=self.other_category,
        )

        # Assign products to user
        UserProduct.objects.create(user=self.user, product=self.product1)
        UserProduct.objects.create(user=self.user, product=self.product2)

        # Create token for authentication
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_get_user_products_authenticated(self):
        response = self.client.get(reverse("account:user-products"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should only return products in Solucionario category
        self.assertEqual(len(response.data), 2)

    def test_get_user_products_unauthenticated(self):
        self.client.credentials()  # Remove authentication
        response = self.client.get(reverse("account:user-products"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_products_empty(self):
        # Create another user with no products
        new_user = User.objects.create_user(
            username="newuser",
            email="new@example.com",
            password="testpass123",
            is_active=True,
        )
        new_token = Token.objects.create(user=new_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {new_token.key}")

        response = self.client.get(reverse("account:user-products"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class TestUserPurchasesView(BaseSetup):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

        # Create some products
        self.product1 = Product.objects.create(
            name="Product 1", price=100, slug="product-1"
        )
        self.product2 = Product.objects.create(
            name="Product 2", price=200, slug="product-2"
        )

        # Create purchases for test user
        self.purchase1 = Sell.objects.create(
            user=self.user, total_cost=100, status=SellStatus.FINISHED
        )
        self.purchase1.products.add(self.product1)

        self.purchase2 = Sell.objects.create(
            user=self.user, total_cost=200, status=SellStatus.FINISHED
        )
        self.purchase2.products.add(self.product2)

        self.purchase3 = Sell.objects.create(
            user=self.user, total_cost=200, status=SellStatus.PENDING
        )

        # Create purchase for another user
        self.other_purchase = Sell.objects.create(
            user=self.user2, total_cost=300, status=SellStatus.FINISHED
        )
        self.other_purchase.products.add(self.product1, self.product2)

    def test_get_user_purchases_authenticated(self):
        """Test authenticated user can retrieve their purchases"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.access}")
        response = self.client.get(reverse("account:user-purchases"))
        data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debe haber dos porque la tercera compra está pendiente
        self.assertEqual(len(data), 2)

    def test_get_user_purchases_unauthenticated(self):
        """Test unauthenticated access is denied"""
        response = self.client.get(reverse("account:user-purchases"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_purchases_empty(self):
        """Test empty response when user has no purchases"""
        # Delete all purchases for test user
        Sell.objects.filter(user=self.user).delete()

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.access}")
        response = self.client.get(reverse("account:user-purchases"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
