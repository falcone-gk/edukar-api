import random
import string

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from helpers.messages import CommentForumNotification, ReplyForumNotification
from helpers.constants import POST_PATH

from notification.models import Notification
from notification.tasks import notify_users
from forum.models import Post, Section, Subsection, Comment, Reply


@receiver(post_save, sender=Post)
def signal_after_post_create(sender, created, instance, **kwargs):

    if not created:
        return

    # Creates a random suffix for slug post title.
    generated_slug = slugify(instance.title)

    random_suffix = ''.join([
        random.choice(string.ascii_letters + string.digits)
        for _ in range(5)
    ])
    generated_slug += '-%s' % random_suffix

    instance.slug = generated_slug
    instance.save()

    # Add author in post participants
    instance.participants.add(instance.author)


@receiver(pre_save, sender=Section)
def create_section_slug(sender, instance, **kwargs):

    generated_slug = slugify(instance.name)

    instance.slug = generated_slug


@receiver(pre_save, sender=Subsection)
def create_subsection_slug(sender, instance, **kwargs):

    generated_slug = slugify(instance.name)

    instance.slug = generated_slug


@receiver(post_save, sender=Comment)
def send_notification_comment(sender, instance, created, **kwargs):

    sender = instance.author
    receiver = instance.post.author

    instance.post.participants.add(sender)

    if (not created) or (sender.pk == receiver.pk):
        return

    source = instance.post
    # notif_type = NotificationTypes.objects.get(type_notif='comment')

    # Send notification to the post owner
    notification = Notification.objects.create(
        sender=sender,
        user=receiver,
        title=CommentForumNotification.TITLE,
        description=CommentForumNotification.DESCRIPTION.format(
            sender.username, source.title),
        source_path=POST_PATH.format(source.section.slug, source.slug)
        # source_id=source,
        # notif_type=notif_type
    )

    notify_users(notification, source)


@receiver(post_save, sender=Reply)
def send_notification_reply(sender, instance, created, **kwargs):

    sender = instance.author
    receiver = instance.comment.author

    instance.comment.post.participants.add(sender)

    if (not created) or (sender.pk == receiver.pk):
        return

    source = instance.comment.post
    # notif_type = NotificationTypes.objects.get(type_notif='reply')

    # Send notification to the post owner
    notification = Notification.objects.create(
        sender=sender,
        user=receiver,
        title=ReplyForumNotification.TITLE,
        description=ReplyForumNotification.DESCRIPTION.format(
            sender.username, source.title),
        source_path=POST_PATH.format(source.section.slug, source.slug)
        # source_id=source,
        # notif_type=notif_type
    )

    notify_users(notification, source)
