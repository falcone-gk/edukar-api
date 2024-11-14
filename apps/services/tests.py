import io
import json
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from services.models import Course, Exams, UnivExamsStructure

# Create your tests here.


class BaseServiceTestCase(TestCase):
    def setUp(self):
        structure_exam = {
            "university": "Universidad Nacional",
            "siglas": "UN",
            "exam_type": "Examen de Admisión",
            "area": "Sociales",
        }

        un_obj = UnivExamsStructure.objects.create(**structure_exam)

        structure_exam = {
            "university": "Universidad Nacional Mayor",
            "siglas": "UNM",
            "exam_type": "Examen de Admisión",
            "area": "Ingeniería",
        }

        unm_obj = UnivExamsStructure.objects.create(**structure_exam)

        self.generate_photo_file()
        exam_data = {
            "title": "UNSA Examen de Admisión Fase II",
            "cover": "test.png",
            "source_exam": "http//:example.com",
            "source_video_solution": "http//:video.example.com",
        }

        self.num_exams_one = 20
        self.list_years_one = [2012 + i for i in range(self.num_exams_one)]

        for i, year in enumerate(self.list_years_one):
            exam_data["title"] = exam_data.get("title") + "-" + str(i)
            Exams.objects.create(root=un_obj, year=year, **exam_data)

        self.num_exams_two = 4
        self.list_years_two = [2012 + i for i in range(self.num_exams_two)]

        for i, year in enumerate(self.list_years_two):
            exam_data["title"] = exam_data.get("title") + "-" + str(i)
            Exams.objects.create(root=unm_obj, year=year, **exam_data)

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

    @patch("utils.services.cloudflare.CloudflarePublicExams.get_exam")
    def test_success_download_exam_by_slug(self, mock_get_exam):
        mock_stream = BytesIO(self.exam_content)  # Simulate a stream
        mock_get_exam.return_value = mock_stream
        exam = Exams.objects.all().latest("pk")

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        response = client.get(
            reverse("services:exam-download", kwargs={"slug": exam.slug})
        )

        # Assertions
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


class TestCoursesList(BaseServiceTestCase):
    def test_success_get_list_courses(self):
        client = APIClient()
        response = client.get(reverse("services:courses-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
