import random
import string

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from forum.models import Post, Section, Subsection

@receiver(pre_save, sender=Post)
def create_post_title_slug(sender, instance, **kwargs):

    # Creates a random suffix for slug post title.
    generated_slug = slugify(instance.title)

    random_suffix = ''.join([
        random.choice(string.ascii_letters + string.digits)
        for i in range(5)
    ])
    generated_slug += '-%s' % random_suffix

    instance.slug = generated_slug

@receiver(pre_save, sender=Section)
def create_section_slug(sender, instance, **kwargs):

    # Creates a random suffix for slug post title.
    generated_slug = slugify(instance.name)

    instance.slug = generated_slug

@receiver(pre_save, sender=Subsection)
def create_subsection_slug(sender, instance, **kwargs):

    # Creates a random suffix for slug post title.
    generated_slug = slugify(instance.name)

    instance.slug = generated_slug