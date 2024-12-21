from account.models import UserProduct
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
        existing = UserProduct.objects.filter(user=user, product__in=products)
        if existing.exists():
            raise serializers.ValidationError(
                "Algunos productos ya fueron comprados."
            )

        return products

    def create(self, validated_data):
        user = self.context["request"].user
        products = validated_data["products"]
        user_products = [
            UserProduct(user=user, product=product) for product in products
        ]
        return UserProduct.objects.bulk_create(user_products)
