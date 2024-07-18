import logging

from django.dispatch import receiver
from djoser.signals import user_registered, user_activated

logger = logging.getLogger(__name__)


@receiver(user_registered)
def handle_registration(sender, user, request, **kwargs):

    logger.info(f"Account registration success user {user.username}")


@receiver(user_activated)
def handle_activation(sender, user, request, **kwargs):

    logger.info(f"Account activation success user {user.username}")
