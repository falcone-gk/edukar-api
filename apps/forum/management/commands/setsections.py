from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from forum.models import Section, Subsection

class Command(BaseCommand):
    help = 'Creates default sections for forum home page'

    def handle(self, *args, **options):

        # Section structure where we define sections that has subsections each.
        sections = [
            {'Cursos': ['Aritmética', 'Algebra', 'Trigonometría', 'Geometría', 'Física', 'Química',
                'Razonamiento Matemático', 'Razonamiento Verbal']}
        ]

        try:
            for section in sections:
                try:
                    section_name = list(section.keys())[0]
                    section_obj = Section(name=section_name)
                    section_obj.save()

                except IntegrityError:
                    # If for some reason the section already exists, then we catch
                    # the error
                    section_obj = Section.objects.get(name=section_name)
                    self.stdout.write("{0} section already exists".format(section_name))

                finally:
                    # In this case the section has subsection, so we create those
                    # subsections and sync to the section.
                    subsections = list(section.values())[0]
                    for subsection in subsections:
                        try:
                            subsection_obj = Subsection(section=section_obj, name=subsection)
                            subsection_obj.save()
                        except IntegrityError:
                            # Raise error in case subsection already exists.
                            self.stdout.write("{0} subsection already exists".format(subsection))

        except Section.DoesNotExist:
            # Raise error when Section model has not been created.
            raise CommandError('Section model does not exist!')

        self.stdout.write(self.style.SUCCESS('Sections and subsection created successfully'))

