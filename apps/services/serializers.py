from django.utils.text import slugify
from rest_framework import serializers
from services.models import Course, Exams


class ExamsSerializer(serializers.ModelSerializer):
    # cover = serializers.CharField(source="cover.url")
    university = serializers.SerializerMethodField()

    class Meta:
        model = Exams
        fields = "__all__"

    def get_university(self, obj):
        if obj.university is None:
            return ""
        return obj.university.name


class ExamFileSerializer(serializers.Serializer):
    exam_file = serializers.FileField()


class UploadExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exams
        fields = (
            "university",
            "type",
            "area",
            "title",
            "cover",
            "year",
            "source_exam",
        )

    def validate(self, data):
        title = data.get("title")
        if title:
            # Generate a slug based on the title
            slug = slugify(title)

            # Ensure the slug is unique
            if Exams.objects.filter(slug=slug).exists():
                raise serializers.ValidationError(
                    {
                        "slug": "The slug already exists. Please provide a unique title."
                    }
                )

            # Add the slug to validated data
            data["slug"] = slug
        else:
            raise serializers.ValidationError(
                {"title": "Title is required to generate a slug."}
            )

        return data


class CoursesSerializer(serializers.ModelSerializer):
    # image = serializers.CharField(source="image.url")

    class Meta:
        model = Course
        fields = "__all__"
