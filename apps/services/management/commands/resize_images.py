import os
from django.core.management.base import BaseCommand
from django.core.files import File
from services.models import Exams


class Command(BaseCommand):
    help = 'Resize existing cover images for exams'

    def handle(self, *args, **kwargs):
        exams = Exams.objects.all()
        for exam in exams:
            if exam.cover:
                cover_path = exam.cover.path
                with open(cover_path, 'rb') as cover_file:
                    # Use Django's File object to wrap the file
                    cover_file_django = File(cover_file)
                    exam.cover.save(os.path.basename(cover_path),
                                    cover_file_django, save=True)

                self.stdout.write(self.style.SUCCESS(
                    f'Successfully resized image for exam: {exam.title}'
                ))
        self.stdout.write(self.style.SUCCESS(
            'Finished resizing images for all exams'))
