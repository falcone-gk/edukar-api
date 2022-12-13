from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):

	def authenticate(self, request, username=None, password=None):

		user_model = get_user_model()

		try:
			user = user_model.objects.get(
				Q(username__iexact=username) | Q(email__iexact=username)
			)

			if not user.is_active:
				return None

			if user.check_password(password):
				return user

		except user_model.DoesNotExist:
			return None