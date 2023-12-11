from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from services.models import Course, Exams, UnivExamsStructure

class ExamStructureSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnivExamsStructure
        fields = '__all__'

class ExamsSerializer(serializers.ModelSerializer):

    root = serializers.SerializerMethodField()
    cover = serializers.CharField(source='cover.url')

    class Meta:
        model = Exams
        fields = '__all__'

    def get_root(self, obj):

        try:
            exam_structure = obj.root
            serializer = ExamStructureSerializer(exam_structure)
            return serializer.data
        except ObjectDoesNotExist:
            return {}

class CoursesSerializer(serializers.ModelSerializer):

    image = serializers.CharField(source='image.url')

    class Meta:
        model = Course
        fields = '__all__'

