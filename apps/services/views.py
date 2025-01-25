from account.permissions import IsProductOwner
from core.paginators import CustomPagination
from dashboard.models import DownloadExams
from django.db import transaction
from django.http import Http404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from services.models import Course, Exams, University
from services.serializers import (
    CoursesSerializer,
    ExamsSerializer,
    ProductVideoPartsSerializer,
    UploadExamSerializer,
)
from store.models import Product, VideoPart

from helpers.choices import ProductTypes
from helpers.responses import get_streaming_response
from utils.services.cloudflare import Cloudflare

# Create your views here.


class ExamsAPIView(generics.ListAPIView):
    serializer_class = ExamsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Exams.objects.filter(is_delete=False)

        # Get query params to filter
        univ = self.request.query_params.get("univ", None)
        year = self.request.query_params.get("year", None)
        _type = self.request.query_params.get("type", None)
        area = self.request.query_params.get("area", None)
        # video_solution = self.request.query_params.get("video", None)

        if (univ is not None) and (univ != ""):
            queryset = queryset.filter(university__siglas=univ)
        if (year is not None) and (year != "0"):
            queryset = queryset.filter(year=year)
        if _type is not None:
            queryset = queryset.filter(type=_type)
        if area is not None:
            queryset = queryset.filter(area=area)

        # TODO add test for this filter
        # if video_solution is not None:
        #     if video_solution == "free":
        #         queryset = queryset.exclude(source_video_solution="")
        #     elif video_solution == "premium":
        #         queryset = queryset.exclude(source_video_solution_premium="")

        return queryset.order_by("-year", "-id")


class RetrieveExamsAPIView(generics.RetrieveAPIView):
    queryset = Exams.objects.filter(is_delete=False)
    serializer_class = ExamsSerializer
    lookup_field = "slug"


class GetExamsFilterAPIView(APIView):
    def get(self, request, format=None, *args, **kwargs):
        universities = University.objects.order_by().values(
            "name", "siglas", "exam_types", "exam_areas"
        )
        years = (
            Exams.objects.filter(is_delete=False)
            .order_by("year")
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
        cf = Cloudflare(user)
        download = DownloadExams.objects.create(exam=exam, user=user)

        try:
            file_stream = cf.get_document(exam_key)
            download.save()
            # Return the file as a downloadable response
            return get_streaming_response(file_stream, slug, "pdf")
        except Exception as error:
            download.download_successful = False
            download.save()
            error_msg = {
                "message": "No se pudo descargar el examen. Avisar a soporte sobre el problema",
                "error": str(error),
            }
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)


class UploadExamAPIView(APIView):
    permission_classes = (IsAdminUser,)

    # TODO: Check nginx send file max size (Send exams files)
    def post(self, request, format=None):
        # serializer_file = ExamFileSerializer(data=request.data)
        # serializer_file.is_valid(raise_exception=True)

        serializer = UploadExamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # file = request.data["exam_file"]
        # cf = Cloudflare()
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


# TODO: Add tests for this endpoint
class ProductVideoPartsView(generics.RetrieveAPIView):
    serializer_class = ProductVideoPartsSerializer
    permission_classes = (IsProductOwner,)

    def get_object(self):
        slug = self.kwargs.get("slug")
        product = Product.objects.filter(
            slug=slug, type=ProductTypes.VIDEO
        ).first()
        if not product:
            raise NotFound("Product not found or is not a video product.")

        self.check_object_permissions(self.request, product)
        return product


# TODO: Add tests for this endpoint
class VideoSignedURLView(generics.RetrieveAPIView):
    permission_classes = [IsProductOwner]  # Add the permission class

    def get_object(self):
        product_slug = self.kwargs.get("slug")
        part_number = self.request.query_params.get("part", 1)

        product = Product.objects.filter(
            slug=product_slug, type=ProductTypes.VIDEO
        ).first()

        if not product:
            raise NotFound("Product not found or is not a video product.")

        self.check_object_permissions(self.request, product)

        try:
            # Get the VideoPart instance based on product slug and part number
            video_part = VideoPart.objects.get(
                product__slug=product_slug, part_number=part_number
            )
        except VideoPart.DoesNotExist:
            raise NotFound("Video part not found for this product.")

        return video_part

    def get(self, request, *args, **kwargs):
        video_part = self.get_object()

        # Initialize the Cloudflare class
        cloudflare = Cloudflare()

        # Get the signed URL for the video
        result = cloudflare.get_video_signed_url(video_part.url)

        # Check if there was an error
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # Return the signed URL
        return Response(result, status=status.HTTP_200_OK)
