from datetime import datetime

from account.models import UserProduct
from core.paginators import CustomPagination
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
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

from helpers.choices import ProductTypes

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

    # TODO: Hacer tests de este endpoint
    @action(detail=True, methods=["get"])
    def recommendations(self, request, slug=None):
        """
        Get recommended products based on the given product.
        """
        try:
            # Fetch the product by slug
            product = Product.objects.get(slug=slug)

            # Logic to find recommended products
            # Example: Products in the same category, excluding the current product
            recommended_products = Product.objects.filter(
                category=product.category
            ).exclude(id=product.id)

            if product.type == ProductTypes.PACKAGE:
                recommended_products = recommended_products.exclude(
                    id__in=product.items.values_list("id", flat=True)
                )

            # Additional filtering based on shared attributes
            shared_attributes = product.product_attributes.values_list(
                "attribute_option", flat=True
            )
            recommended_products = recommended_products.filter(
                product_attributes__attribute_option__in=shared_attributes
            ).distinct()

            # Get only the last four recommended products
            recommended_products = recommended_products.order_by("-id")[:4]

            # Serialize the recommendations
            serializer = self.get_serializer(recommended_products, many=True)
            return Response(serializer.data)

        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=404)


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


class CheckProductPurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    # TODO: Agregar tests de endpoint
    def post(self, request, format=None):
        user = request.user
        product_identifier = request.data.get("identifier")

        # Validar que se recibió un ID de producto
        if not product_identifier:
            return Response(
                {"error": "El campo 'identifier' es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Obtener el producto
        product = get_object_or_404(Product, identifier=product_identifier)

        # Verificar si el producto principal es de compra única
        if product.is_one_time_purchase:
            # Comprobar si el usuario ya compró este producto
            already_purchased = UserProduct.objects.filter(
                user=user, product=product
            ).exists()
            if already_purchased:
                return Response(
                    {"message": "El producto ya ha sido comprado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Filtrar los items que son de compra única
        one_time_items = product.items.filter(
            category__is_one_time_purchase=True
        )

        # Verificar si alguno de los items ya ha sido comprado
        if one_time_items.exists():
            purchased_items = UserProduct.objects.filter(
                user=user, product__in=one_time_items
            )
            if purchased_items.exists():
                return Response(
                    {
                        "message": "Ya has comprado uno de los productos del paquete."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Producto y sus items no comprados, o no son de compra única
        return Response(
            {"message": "El producto puede ser añadido al carrito."},
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
