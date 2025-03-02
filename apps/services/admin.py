from django.contrib import admin
from django.core.exceptions import ValidationError
from services.models import Course, Exams, University

# Register your models here.


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("name", "siglas")
    search_fields = ("name", "siglas")
    list_filter = ("siglas",)
    ordering = ("name",)


@admin.register(Exams)
class ExamsAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "university",
        "type",
        "area",
        "year",
        "is_delete",
    )
    search_fields = ("title", "university__name", "type", "area", "year")
    list_filter = ("university", "type", "area", "year", "is_delete")
    ordering = ("-year", "title")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("university",)

    fieldsets = (
        (
            "Exam Details",
            {
                "fields": (
                    "university",
                    "type",
                    "area",
                    "title",
                    "slug",
                    "year",
                    "is_delete",
                    "cover",
                )
            },
        ),
        (
            "Source Information",
            {
                "fields": (
                    "source_exam",
                    "source_video_solution",
                    "source_video_solution_premium",
                ),
                "classes": ("collapse",),  # Collapsible section
            },
        ),
        (
            "Related Products",
            {
                "fields": ("products",),
            },
        ),
    )

    filter_horizontal = ("products",)

    def save_model(self, request, obj, form, change):
        """Ensure exam type and area are valid before saving."""
        if obj.university:
            if obj.type not in obj.university.exam_types:
                raise ValidationError(
                    f"The type '{obj.type}' is not valid for the university '{obj.university.name}'. "
                    f"Allowed types: {', '.join(obj.university.exam_types)}."
                )
            if obj.area and obj.area not in obj.university.exam_areas:
                raise ValidationError(
                    f"The area '{obj.area}' is not valid for the university '{obj.university.name}'. "
                    f"Allowed areas: {', '.join(obj.university.exam_areas)}."
                )
        super().save_model(request, obj, form, change)


class CoursesAdmin(admin.ModelAdmin):
    list_display = ("name",)


# admin.site.register(University, UniversityAdmin)
# admin.site.register(Exams, ExamsAdmin)
admin.site.register(Course, CoursesAdmin)
