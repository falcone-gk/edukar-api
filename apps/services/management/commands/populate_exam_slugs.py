from django.core.management.base import BaseCommand
from django.utils.text import slugify
from services.models import Exams


class Command(BaseCommand):
    help = 'Populate the slug field for existing exams based on the title'

    def handle(self, *args, **kwargs):
        exams = Exams.objects.all()
        for exam in exams:
            if not exam.slug:
                exam.slug = slugify(f"{exam.title} - {exam.root.area}")
                exam.save()
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully updated slug for exam: {exam.title}'
                ))
        self.stdout.write(
            self.style.SUCCESS('Finished populating slugs for all exams')
        )
