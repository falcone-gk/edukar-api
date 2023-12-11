from django.contrib import admin
from services.models import Course, UnivExamsStructure, Exams

# Register your models here.

class UnivExamsStructureAdmin(admin.ModelAdmin):
    list_display = ('university', 'siglas', 'exam_type')

class ExamsAdmin(admin.ModelAdmin):
    list_display = ('root', 'title', 'year')

class CoursesAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(UnivExamsStructure, UnivExamsStructureAdmin)
admin.site.register(Exams, ExamsAdmin)
admin.site.register(Course, CoursesAdmin)

