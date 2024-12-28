from django.contrib import admin
from services.models import Course, Exams, University

# Register your models here.


class UniversityAdmin(admin.ModelAdmin):
    list_display = ("name", "siglas")


class ExamsAdmin(admin.ModelAdmin):
    list_display = ("university", "title", "type", "area", "year")


class CoursesAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(University, UniversityAdmin)
admin.site.register(Exams, ExamsAdmin)
admin.site.register(Course, CoursesAdmin)
