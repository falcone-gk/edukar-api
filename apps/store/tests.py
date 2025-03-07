import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from services.models import Exams, University
from store.models import Attribute, AttributeOption, Category, Product

from helpers.choices import ProductTypes

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

        exam_data = {
            "cover": "test.png",
            "source_exam": "http//:example.com",
            "source_video_solution": "http//:video.example.com",
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

        # Set up initial data
        self.category = Category.objects.create(
            name="Solucionario", is_one_time_purchase=True
        )
        self.attribute_univ = Attribute.objects.create(
            name="Universidad", category=self.category
        )
        # self.attribute_size = Attribute.objects.create(
        #     name="Size", category=self.category
        # )

        # Create attribute options
        AttributeOption.objects.create(
            attribute=self.attribute_univ, value="Universidad Nacional Mayor"
        )
        AttributeOption.objects.create(
            attribute=self.attribute_univ,
            value="Universidad Nacional San Agustín",
        )


class TestSellProducts(BaseServiceTestCase):
    def setUp(self):
        super().setUp()

        self.json_form = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "testuser",
            "last_name": "testuser",
            "password": "testpassword",
        }

        # Create user and its token
        self.user = User.objects.create_user(**self.json_form)
        token, _ = Token.objects.get_or_create(user=self.user)
        self.access = token.key

        product1_data = {
            "type": ProductTypes.DOCUMENT,
            "name": "Producto 1",
            "description": "Descripcion 1",
            "price": "10.00",
            "source": "https://test.com/file/file.pdf/",
            "category_id": self.category.id,
        }
        self.product_1 = Product.objects.create(**product1_data)

        product2_data = {
            "type": ProductTypes.DOCUMENT,
            "name": "Producto 2",
            "description": "Descripcion 2",
            "price": "30.00",
            "source": "https://test.com/file/file.pdf/",
            "category_id": self.category.id,
        }
        self.product_2 = Product.objects.create(**product2_data)

        product3_data = {
            "type": ProductTypes.PACKAGE,
            "name": "Package 1",
            "description": "Descripcion 1 package",
            "price": "35.00",
            "category_id": self.category.id,
        }
        self.product_3 = Product.objects.create(**product3_data)
        self.product_3.items.add(self.product_1, self.product_2)

    def test_success_list_products(self):
        client = APIClient()
        res = client.get(
            reverse("store:product-list"),
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_success_get_product(self):
        client = APIClient()
        res = client.get(
            reverse(
                "store:product-detail", kwargs={"slug": self.product_1.slug}
            ),
        )
        data = json.loads(res.content)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], self.product_1.name)

    def test_success_get_package(self):
        client = APIClient()
        url = reverse(
            "store:product-detail", kwargs={"slug": self.product_3.slug}
        )
        res = client.get(url)
        data = json.loads(res.content)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], self.product_3.name)

    def test_success_add_product_to_cart(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.post(
            reverse("store:add-item-cart"),
            {"product": self.product_1.id},
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_success_add_package_to_cart(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        res = client.post(
            reverse("store:add-item-cart"),
            {"package": self.product_3.id},
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_error_product_already_in_cart(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        client.post(
            reverse("store:add-item-cart"),
            {"product": self.product_1.id},
        )

        res = client.post(
            reverse("store:add-item-cart"),
            {"product": self.product_1.id},
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_package_has_one_purchase_product_already_in_cart(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
        client.post(
            reverse("store:add-item-cart"),
            {"product": self.product_1.id},
        )

        res = client.post(
            reverse("store:add-item-cart"),
            {"product": self.product_3.id},
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_success_remove_product_from_user_cart(self):
    #     client = APIClient()
    #     client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
    #     client.post(
    #         reverse("store:add-item-cart"),
    #         {"product": self.product_1.id},
    #     )

    #     res = client.post(
    #         reverse("store:remove-item-cart"),
    #         {"product": self.product_1.id},
    #     )

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)

    #     user_cart, _ = Sell.get_user_cart(user=self.user)
    #     item_in_cart = user_cart.products.filter(id=self.product_1.id).exists()
    #     self.assertFalse(item_in_cart)

    # def test_success_remove_package_from_user_cart(self):
    #     client = APIClient()
    #     client.credentials(HTTP_AUTHORIZATION="Token " + self.access)
    #     client.post(
    #         reverse("store:add-item-cart"),
    #         {"package": self.product_3.id},
    #     )

    #     res = client.post(
    #         reverse("store:remove-item-cart"),
    #         {"package": self.product_3.id},
    #     )

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)

    #     user_cart, _ = Sell.get_user_cart(user=self.user)
    #     item_in_cart = user_cart.products.filter(id=self.product_3.id).exists()
    #     self.assertFalse(item_in_cart)
