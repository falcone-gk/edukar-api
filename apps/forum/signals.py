import random
import string

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from notification.models import NotificationTypes, Notification
from notification.tasks import notify_user
from forum.models import Post, Section, Subsection, Comment, Reply

@receiver(post_save, sender=Post)
def create_post_title_slug(sender, created, instance, **kwargs):

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

@receiver(pre_save, sender=Section)
def create_section_slug(sender, instance, **kwargs):

    generated_slug = slugify(instance.name)

    instance.slug = generated_slug

@receiver(pre_save, sender=Subsection)
def create_subsection_slug(sender, instance, **kwargs):

    generated_slug = slugify(instance.name)

    instance.slug = generated_slug

@receiver(post_save, sender=Comment)
def send_notification(sender, instance, created, **kwargs):

    sender = instance.author
    receiver = instance.post.author

    if (not created) or (sender.pk == receiver.pk):
        return

    source = instance.post
    notif_type = NotificationTypes.objects.get(type_notif='comment')

    # Send notification to the post owner
    Notification.objects.create(
        sender=sender,
        user=receiver,
        source_id=source,
        notif_type=notif_type
    )

@receiver(post_save, sender=Reply)
def send_notification(sender, instance, created, **kwargs):

    sender = instance.author
    receiver = instance.comment.author

    if (not created) or (sender.pk == receiver.pk):
        return

    source = instance.comment.post
    notif_type = NotificationTypes.objects.get(type_notif='reply')

    # Send notification to the post owner
    Notification.objects.create(
        sender=sender,
        user=receiver,
        source_id=source,
        notif_type=notif_type
    )