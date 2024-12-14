from datetime import datetime

from core.paginators import CustomPagination
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from store.models import Category, Product, Sell
from store.serializers import (
    AddCartValidationSerializer,
    CartSerializer,
    CategorySerializer,
    ProductSerializer,
    UserProductBulkCreateSerializer,
)

# Create your views here.


class CategoryFiltersAPIView(APIView):
    def get(self, request, format=None):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)


class ProductViewSet(ReadOnlyModelViewSet):
    pagination_class = CustomPagination
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Product.objects.all().order_by("-id")
        query_params = self.request.query_params
        category = query_params.get("category", None)
        attribute_params = {
            key: value
            for key, value in query_params.items()
            if key not in ["page", "size", "category"]
        }
        # Filter by category if provided
        if category:
            queryset = queryset.filter(category_id=category)

        # Apply filters for attributes dynamically
        if attribute_params:
            for attr, value in attribute_params.items():
                # Filter for each attribute key-value pair
                queryset = queryset.filter(
                    product_attributes__attribute_option__attribute__label=attr,
                    product_attributes__attribute_option__value=value,
                )

        return queryset


class AddItemCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AddCartValidationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        product = data.get("product", None)

        user = self.request.user
        user_cart, _ = Sell.get_user_cart(user=user)
        user_cart.on_cart_at = datetime.now(tz=timezone.utc)
        if product is not None:
            user_cart.products.add(product)

        user_cart.total_cost = user_cart.get_total_cost()
        user_cart.save()

        cart_serializer = CartSerializer(user_cart)
        # Aquí puedes añadir lógica para guardar el carrito si es necesario
        return Response(
            cart_serializer.data,
            status=status.HTTP_200_OK,
        )


class RemoveItemCartAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_cart(self):
        user = self.request.user
        user_cart, _ = Sell.get_user_cart(user=user)
        return user_cart

    def post(self, request, *args, **kwargs):
        data = request.data
        product = data.get("product", None)
        user_cart = self.get_cart()

        if product is not None:
            user_cart.products.remove(product)

        cart_serializer = CartSerializer(user_cart)

        return Response(
            cart_serializer.data,
            status=status.HTTP_200_OK,
        )


class UserProductBulkCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UserProductBulkCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        msg = "Tus productos fueron añadidos exitosamente."
        return Response(
            {"message": msg},
            status=status.HTTP_201_CREATED,
        )
