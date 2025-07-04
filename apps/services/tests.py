import io
import json
from io import BytesIO
from unittest.mock import patch

from dashboard.models import DownloadExams
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from services.models import Course, Exams, University

# Create your tests here.


class BaseServiceTestCase(TestCase):
    def setUp(self):
        structure_exam = {
            "name": "Universidad Nacional",
            "siglas": "UN",
            "exam_types": ["Ordinario", "CEPRE"],
            "exam_areas": ["Social", "Medicina"],
        }

        self.un_obj = University.objects.create(**structure_exam)

        structure_exam = {
            "name": "Universidad Nacional Mayor",
            "siglas": "UNM",
            "exam_types": ["Ordinario", "CEPRE San Marco"],
            "exam_areas": ["Letras", "Ingeniería", "Medicina"],
        }

        unm_obj = University.objects.create(**structure_exam)

        self.generate_photo_file()
        exam_data = {
            # "title": "UNSA Examen de Admisión Fase II",
            "cover": "test.png",
            "source_exam": "http//:example.com",
            "source_video_solution": "http://video.example.com",
        }
        title = "UNSA Examen de Admisión Fase II"

        self.num_exams_one = 20
        self.list_years_one = [2012 + i for i in range(self.num_exams_one)]

        for i, year in enumerate(self.list_years_one):
            current_title = title + "-" + str(i)
            Exams.objects.create(
                university=self.un_obj,
                type="Ordinario",
                area="Social",
                year=year,
                title=current_title,
                slug=slugify(current_title),
                **exam_data,
            )

        self.num_exams_two = 4
        self.list_years_two = [2012 + i for i in range(self.num_exams_two)]

        for i, year in enumerate(self.list_years_two):
            current_title = title + "-" + str(i) + "part 2"
            Exams.objects.create(
                university=unm_obj,
                title=current_title,
                type="Ordinario",
                area="Letras",
                year=year,
                slug=slugify(current_title),
                **exam_data,
            )

        self.num_exams = self.num_exams_one + self.num_exams_two

        # Course creation
        self.course = Course.objects.create(
            name="Polinomios", image="test.png", url="http//:udemy.com"
        )

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        return file


class TestCreateExams(BaseServiceTestCase):
    def setUp(self):
        self.exam_data = {
            "title": "UNSA Examen de Admisión Fase II",
            "cover": "test.png",
            "source_exam": "http//:example.com",
            "source_video_solution": "http://video.example.com",
            "slug": "unsa-examen-de-admision-fase-ii",
        }
        return super().setUp()

    def test_success_create_exam_with_area_and_type(self):
        exam = Exams.objects.create(
            university=self.un_obj,
            type="Ordinario",
            area="Social",
            year=2024,
            **self.exam_data,
        )
        self.assertIsInstance(exam, Exams)

    def test_success_create_exam_with_no_area(self):
        exam = Exams.objects.create(
            university=self.un_obj,
            type="Ordinario",
            year=2024,
            **self.exam_data,
        )
        self.assertIsInstance(exam, Exams)

    def test_error_create_exam_wrong_type(self):
        with self.assertRaises(ValidationError):
            Exams.objects.create(
                university=self.un_obj,
                type="wrong_type",  # Invalid type
                year=2024,
                **self.exam_data,
            )

    def test_error_create_exam_wrong_area(self):
        with self.assertRaises(ValidationError):
            Exams.objects.create(
                university=self.un_obj,
                type="Ordinario",
                area="wrong_area",  # Invalid area
                year=2024,
                **self.exam_data,
            )


class TestListExams(BaseServiceTestCase):
    size_per_page = 8

    def test_success_get_list_all_exams(self):
        client = APIClient()
        res = client.get(
            reverse("services:exams-list")
            + "?size={}".format(self.size_per_page)
        )

        json_res = json.loads(res.content)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json_res["count"], self.num_exams)
        self.assertEqual(len(json_res["results"]), self.size_per_page)

    def test_success_filter_by_university(self):
        client = APIClient()
        res = client.get(
            reverse("services:exams-list")
            + "?size={0}&univ={1}".format(self.size_per_page, "UNM")
        )

        json_res = json.loads(res.content)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json_res["count"], self.num_exams_two)

    def test_filter_values_not_found(self):
        client = APIClient()
        res = client.get(
            reverse("services:exams-list")
            + "?size={0}&univ={1}".format(self.size_per_page, "wrong_name")
        )

        json_res = json.loads(res.content)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json_res["count"], 0)

    def test_get_filter_exams_success(self):
        client = APIClient()
        res = client.get(reverse("services:exams-filters"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestRetrieveExam(BaseServiceTestCase):
    def setUp(self):
        json_form = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "testuser",
            "last_name": "testuser",
            "password": "testpassword",
        }

        # Creating user and user profile
        self.user = User.objects.create_user(**json_form)

        # Getting user token
        token, _ = Token.objects.get_or_create(user=self.user)
        self.access = token.key

        # exam mockup
        self.exam_content = b"%PDF-1.4\nSample PDF Content"  # Mock PDF content
        return super().setUp()

    def test_success_get_exam_by_slug(self):
        exam = Exams.objects.all().latest("pk")
        client = APIClient()
        res = client.get(
            reverse("services:exam-retrieve", kwargs={"slug": exam.slug})
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @patch("utils.services.cloudflare.Cloudflare.get_document")
    def test_success_download_exam_by_slug(self, mock_get_exam):
        mock_stream = BytesIO(self.exam_content)  # Simulate a stream
        mock_get_exam.return_value = mock_stream
        exam = Exams.objects.all().latest("pk")

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        response = client.get(
            reverse("services:exam-download", kwargs={"slug": exam.slug})
        )

        download = DownloadExams.objects.latest("id")
        # Assertions
        self.assertEqual(download.exam.id, exam.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment; filename=", response["Content-Disposition"])
        self.assertEqual(
            response["Content-Disposition"],
            f"attachment; filename={exam.slug}.pdf",
        )
        streamed_content = b"".join(response.streaming_content)
        self.assertEqual(streamed_content, self.exam_content)

    def test_error_auth_download_exam_by_slug(self):
        exam = Exams.objects.all().latest("pk")

        client = APIClient()
        response = client.get(
            reverse("services:exam-download", kwargs={"slug": exam.slug})
        )

        # Assertions
        self.assertEqual(response.status_code, 401)

    @patch("utils.services.cloudflare.Cloudflare")
    def test_error_download_r2_bucket_failed(self, mock_cloudflare):
        mock_instance = mock_cloudflare.return_value
        mock_instance.get_document.side_effect = ValueError("random error")
        exam = Exams.objects.all().latest("pk")

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        response = client.get(
            reverse("services:exam-download", kwargs={"slug": exam.slug})
        )
        download = DownloadExams.objects.latest("id")
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(content, dict)
        self.assertFalse(download.download_successful)


class TestCoursesList(BaseServiceTestCase):
    def test_success_get_list_courses(self):
        client = APIClient()
        response = client.get(reverse("services:courses-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
