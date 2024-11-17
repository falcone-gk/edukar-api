from core.paginators import CustomPagination
from django.db import transaction
from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from services.models import Course, Exams, University
from services.serializers import (
    CoursesSerializer,
    ExamsSerializer,
    UploadExamSerializer,
)

from helpers.responses import get_streaming_response
from utils.services.cloudflare import CloudflarePublicExams

# Create your views here.


class ExamsAPIView(generics.ListAPIView):
    serializer_class = ExamsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Exams.objects.filter(is_delete=False)

        # Get query params to filter
        univ = self.request.query_params.get("univ")
        year = self.request.query_params.get("year")
        video_solution = self.request.query_params.get("video", None)

        if (univ is not None) and (univ != ""):
            queryset = queryset.filter(university__siglas=univ)
        if (year is not None) and (year != "0"):
            queryset = queryset.filter(year=year)
        # TODO add test for this filter
        if video_solution is not None:
            if video_solution == "free":
                queryset = queryset.exclude(source_video_solution="")
            elif video_solution == "premium":
                queryset = queryset.exclude(source_video_solution_premium="")

        return queryset.order_by("-year", "-id")


class RetrieveExamsAPIView(generics.RetrieveAPIView):
    queryset = Exams.objects.filter(is_delete=False)
    serializer_class = ExamsSerializer
    lookup_field = "slug"


class GetExamsFilterAPIView(APIView):
    def get(self, request, format=None, *args, **kwargs):
        universities = (
            University.objects.order_by().values("name", "siglas").distinct()
        )
        years = (
            Exams.objects.order_by("year")
            .values_list("year", flat=True)
            .distinct()
        )

        data = {"universities": universities, "years": years}

        return Response(data, status=status.HTTP_200_OK)


class DownloadExamAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, slug):
        try:
            return Exams.objects.get(slug=slug)
        except Exams.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        user = self.request.user
        exam = self.get_object(slug)
        exam_key = exam.source_exam
        cf = CloudflarePublicExams(user)

        try:
            file_stream = cf.get_exam(exam_key)
            # Return the file as a downloadable response
            return get_streaming_response(file_stream, slug, "pdf")
        except Exception as error:
            error_msg = {
                "message": "No se pudo descargar el examen. Avisar a soporte sobre el problema",
                "error": str(error),
            }
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)


class UploadExamAPIView(APIView):
    permission_classes = (IsAdminUser,)

    # TODO: Add test for this endpoint
    # TODO: Check nginx send file max size (Send exams files)
    def post(self, request, format=None):
        # serializer_file = ExamFileSerializer(data=request.data)
        # serializer_file.is_valid(raise_exception=True)

        serializer = UploadExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # file = request.data["exam_file"]
        # cf = CloudflarePublicExams()
        try:
            with transaction.atomic():
                serializer.save()
                # cf.put_exam(file, serializer.data["source_exam"])
        except Exception as error:
            error_msg = {
                "message": "Hubo error al subir examen a CF o a la BD",
                "error": str(error),
            }
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Examen fue creado exitosamente"},
            status=status.HTTP_201_CREATED,
        )


class CoursesAPIView(generics.ListAPIView):
    serializer_class = CoursesSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        params = self.request.query_params.get("search")
        if params:
            queryset = Course.objects.filter(name__in=params)

        else:
            queryset = Course.objects.all()

        return queryset.order_by("id")
