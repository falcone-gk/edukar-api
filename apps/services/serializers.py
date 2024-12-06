from account.models import UserProduct
from django.utils.text import slugify
from rest_framework import serializers
from services.models import Course, Exams, Package, Product, Sell


class ExamsSerializer(serializers.ModelSerializer):
    cover = serializers.CharField(source="cover.url")
    university = serializers.SerializerMethodField()

    class Meta:
        model = Exams
        fields = "__all__"

    def get_university(self, obj):
        if obj.university is None:
            return ""
        return obj.university.name


class ExamFileSerializer(serializers.Serializer):
    exam_file = serializers.FileField()


class UploadExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exams
        fields = (
            "university",
            "type",
            "area",
            "title",
            "cover",
            "year",
            "source_exam",
        )

    def validate(self, data):
        title = data.get("title")
        if title:
            # Generate a slug based on the title
            slug = slugify(title)

            # Ensure the slug is unique
            if Exams.objects.filter(slug=slug).exists():
                raise serializers.ValidationError(
                    {
                        "slug": "The slug already exists. Please provide a unique title."
                    }
                )

            # Add the slug to validated data
            data["slug"] = slug
        else:
            raise serializers.ValidationError(
                {"title": "Title is required to generate a slug."}
            )

        return data


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "type",
            "product_image",
            "is_one_time_purchase",
        )


class PackageSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "products",
            "id",
            "name",
            "description",
            "price",
        )


class CartSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    packages = PackageSerializer(many=True, read_only=True)

    class Meta:
        model = Sell
        fields = (
            "products",
            "packages",
            "status",
            "payment_image",
            "total_cost",
            "on_cart_at",
            "on_pending_at",
            "paid_at",
        )


class AddCartValidationSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=False
    )
    package = serializers.PrimaryKeyRelatedField(
        queryset=Package.objects.all(), required=False
    )

    def validate_product(self, product):
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

        return product

    def validate_package(self, package):
        user = self.context["request"].user
        if package is None:
            return package

        products = package.products.all()

        cart, _ = Sell.get_user_cart(user=user)
        if cart is None:
            return package

        for product in products:
            if not product.is_one_time_purchase:
                continue

            is_owned_by_user = cart.products.filter(id=product.id).exists()
            if is_owned_by_user:
                raise serializers.ValidationError(
                    "Tu paquete incluye productos que ya compraste o está en tu carrito."
                )

        return package


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


class CoursesSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source="image.url")

    class Meta:
        model = Course
        fields = "__all__"
