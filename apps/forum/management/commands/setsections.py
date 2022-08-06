from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from forum.models import Section, Subsection

class Command(BaseCommand):
    help = 'Creates default sections for forum home page'

    def handle(self, *args, **options):

        # Section structure where we define sections that has subsection and others that
        # doesn't. Later this list must be as json file.
        sections = [
            'Artículos y Noticias',
            {'Cursos': ['Aritmética', 'Algebra', 'Trigonometría', 'Geometría', 'Física', 'Química',
                'Razonamiento Matemático', 'Razonamiento Verbal']}
        ]

        try:
            for section in sections:
                try:
                    if isinstance(section, str):
                        section_name = section
                        section_obj = Section(name=section_name)
                        section_obj.save()
                    else:
                        section_name = list(section.keys())[0]
                        section_obj = Section(name=section_name)
                        section_obj.save()

                        # In this case the section has subsection, so we create those
                        # subsections and sync to the section.
                        for subsection in section.values():
                            subsection_obj = Subsection(section=section_obj, name=subsection)
                            subsection_obj.save()
                except IntegrityError:
                    # If for some reason the section already exists, then we catch
                    # the error
                    self.stdout.write("{0} section already exists".format(section_name))

        except Section.DoesNotExist:
            # Raise error when Section model has not been created.
            raise CommandError('Section model does not exist!')

        self.stdout.write(self.style.SUCCESS('Sections and subsection created successfully'))

