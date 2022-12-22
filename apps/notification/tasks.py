from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings

from forum.models import Post
from notification.models import NotificationTypes

def notify_user(sender_id, receiver_id, post_source_id, notif_type_id):
    # lookup user by id and send them a message

    sender = User.objects.get(pk=sender_id)
    receiver = User.objects.get(pk=receiver_id)
    post_source = Post.objects.get(pk=post_source_id)
    notif_type = NotificationTypes.objects.get(pk=notif_type_id)

    post_url = f'http://{settings.DOMAIN}/forum/post/{post_source.slug}'
    context = {
        'user_receiver': receiver.username,
        'user_sender': sender.username,
        'descr_receiver': notif_type.desc_receiver,
        'post_title': post_source.title,
        'post_url': post_url
    }

    html_message = render_to_string('notification/notif_answer.html', context)
    message = render_to_string('notification/notif_answer.txt', context)

    receiver.email_user(
        subject='Notificación de Edukar',
        message=message,
        html_message=html_message
    )