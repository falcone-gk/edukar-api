# from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mass_mail

from huey.contrib.djhuey import task

# from forum.models import Post

@task()
def notify_user(notification, post):

    sender = notification.sender
    # post = Post.objects.get(pk=post_source_id)
    users_data = post.participants.exclude(pk=sender.id).values("username", "email")
    # post_url = f'http://{settings.DOMAIN}/{notification.source_path}'
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

    send_mass_mail(messages, fail_silently=False)
