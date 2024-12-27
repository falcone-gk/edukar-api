from decimal import Decimal

from account.models import UserProduct
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from store.models import Attribute, AttributeOption, Category, Product, Sell

from helpers.choices import ProductTypes


class AttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeOption
        fields = ["id", "label", "value"]


class AttributeSerializer(serializers.ModelSerializer):
    options = AttributeOptionSerializer(many=True)

    class Meta:
        model = Attribute
        fields = ["id", "name", "label", "options"]


class CategorySerializer(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True)

    class Meta:
        model = Category
        fields = ["id", "name", "attributes"]


class ProductSerializer(serializers.ModelSerializer):
    """Serializer used in store view"""

    items = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "category",
            "price",
            "show",
            "type",
            "product_image",
            "is_one_time_purchase",
            "items",
            "identifier",
        )

    def get_items(self, obj):
        # This is required to avoid infinite loop
        # we are letting only packages to return their item list
        if obj.type != ProductTypes.PACKAGE:
            return []

        return ProductSerializer(obj.items.all(), many=True).data


class PrivateProductSerializer(serializers.ModelSerializer):
    """Serializer to use for user products purchased"""

    class Meta:
        model = Product
        fields = ("slug", "name", "description", "source", "type")


class AddCartValidationSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=False
    )

    def validate_product(self, product: Product):
        user = self.context["request"].user
        if product is None:
            return product

        if not product.is_one_time_purchase:
            return product

        cart, _ = Sell.get_user_cart(user=user)
        if cart is None:
            return product

        is_owned_by_user = cart.products.filter(id=product.id).exists()
        if is_owned_by_user:
            raise serializers.ValidationError(
                "Ya obtuviste el producto o ya está en tu carrito."
            )

        if product.type != ProductTypes.PACKAGE:
            return product

        for item in product.items.all():
            if not item.is_one_time_purchase:
                continue

            is_owned_by_user = cart.products.filter(id=item.id).exists()
            if is_owned_by_user:
                raise serializers.ValidationError(
                    "Tu paquete incluye productos que ya compraste o está en tu carrito."
                )

        return product


class CartSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Sell
        fields = (
            "products",
            "status",
            "payment_image",
            "total_cost",
            "on_cart_at",
            "on_pending_at",
            "paid_at",
        )


class UserProductBulkCreateSerializer(serializers.Serializer):
    products = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=Product.objects.all()
        ),
        allow_empty=False,
    )

    def validate_products(self, products):
        user = self.context["request"].user

        for product in products:
            UserProduct.validate_product_purchase(user, product)

        return products

    def create(self, validated_data):
        user = self.context["request"].user
        products = validated_data["products"]
        user_products = []

        for product in products:
            if product.type == ProductTypes.PACKAGE:
                # If the product is a package, add its items instead
                package_items = product.items.all()
                user_products.extend(
                    [
                        UserProduct(user=user, product=item)
                        for item in package_items
                    ]
                )
            else:
                # Add non-package products directly
                user_products.append(UserProduct(user=user, product=product))

        try:
            with transaction.atomic():
                # Bulk create UserProduct entries
                instances = UserProduct.objects.bulk_create(user_products)

                # Obteniendo precio total
                total_cost = Decimal("0.00")
                for prod in products:
                    total_cost += prod.price

                # Create Sell instance and link products
                sell = Sell.objects.create(
                    user=user, paid_at=timezone.now(), total_cost=total_cost
                )
                sell.products.add(*products)

            return instances

        except Exception as error:
            error_msg = {
                "message": "Hubo un error al realizar la venta.",
                "error": str(error),
            }
            raise serializers.ValidationError(error_msg)


class SellSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Sell
        fields = ["products", "total_cost", "paid_at"]
