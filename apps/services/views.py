from core.paginators import CustomPagination
from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from services.models import Course, Exams, UnivExamsStructure
from services.serializers import CoursesSerializer, ExamsSerializer

from helpers.responses import get_streaming_response
from utils.services.cloudflare import CloudflarePublicExams

# Create your views here.


class ExamsAPIView(generics.ListAPIView):
    serializer_class = ExamsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Exams.objects.all()

        # Get query params to filter
        univ = self.request.query_params.get("univ")
        year = self.request.query_params.get("year")
        video_solution = self.request.query_params.get("video", None)

        if (univ is not None) and (univ != ""):
            queryset = queryset.filter(root__siglas=univ)
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
    queryset = Exams.objects.all()
    serializer_class = ExamsSerializer
    lookup_field = "slug"


class GetExamsFilterAPIView(APIView):
    def get(self, request, format=None, *args, **kwargs):
        universities = (
            UnivExamsStructure.objects.order_by()
            .values("university", "siglas")
            .distinct()
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
        except Exception:
            error_msg = {
                "error": "No se pudo descargar el examen. Avisar a soporte sobre el problema"
            }
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)


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
