from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from services.models import Exams


@receiver(post_save, sender=Exams)
def signal_after_exam_create(sender, created, instance, **kwargs):

    if not created:
        return

    instance.slug = slugify(f"{instance.title} - {instance.root.area}")
    instance.save()
