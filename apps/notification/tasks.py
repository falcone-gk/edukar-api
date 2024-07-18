from django.template.loader import render_to_string
from django.core.mail import send_mass_mail

from huey.contrib.djhuey import task
import logging

logger = logging.getLogger(__name__)


@task()
def notify_users(notification, post):

    sender = notification.sender
    users_data = post.participants.exclude(
        pk=sender.id).values("username", "email")
    post_url = notification.full_source_path

    messages = []
    for user in users_data:
        username = user.get('username')
        email = user.get('email')
        context = {
            'user_receiver': username,
            'user_sender': sender.username,
            'post_title': post.title,
            'post_url': post_url
        }
        message = render_to_string('notification/notif_answer.txt', context)
        email_message = [
            "Notificación de Edukar",
            message,
            None,
            [email,]
        ]
        messages.append(email_message)

    logger.info(
        "Notification notify_users Enviando emails masivos de user_id "
        f"{sender.pk} con descripcion {notification.description}"
    )
    send_mass_mail(messages, fail_silently=False)
