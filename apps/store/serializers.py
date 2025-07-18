import logging
import re
from decimal import Decimal

from account.models import UserProduct
from account.serializers import AuthorSerializer
from django.core.files.base import ContentFile
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import serializers
from store.models import (
    Attribute,
    AttributeOption,
    Category,
    Claim,
    Product,
    ProductComment,
    Sell,
)
from weasyprint import HTML

from helpers.choices import ProductTypes
from utils.services.culqi import Culqi

logger = logging.getLogger(__name__)


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


class ProductCommentSerializer(serializers.ModelSerializer):
    user = AuthorSerializer()

    class Meta:
        model = ProductComment
        fields = ["user", "comment", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    """Serializer used in store view"""

    items = serializers.SerializerMethodField()
    comments = ProductCommentSerializer(many=True)

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
            "comments",
        )

    def get_items(self, obj):
        # This is required to avoid infinite loop
        # we are letting only packages to return their item list
        if obj.type != ProductTypes.PACKAGE:
            return []

        return ProductSerializer(
            obj.items.all(), many=True, context=self.context
        ).data


class PrivateProductSerializer(serializers.ModelSerializer):
    """Serializer to use for user products purchased"""

    date = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("slug", "name", "description", "source", "date", "type")

    def get_date(self, obj):
        # obj is a Product instance, so we need to find the corresponding UserProduct
        user = self.context["request"].user
        user_product = UserProduct.objects.filter(
            user=user, product=obj
        ).first()
        return user_product.date if user_product else None


class ProductCreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        fields = ["comment"]


# class AddCartValidationSerializer(serializers.Serializer):
#     product = serializers.PrimaryKeyRelatedField(
#         queryset=Product.objects.all(), required=False
#     )

#     def validate_product(self, product: Product):
#         user = self.context["request"].user
#         if product is None:
#             return product

#         if not product.is_one_time_purchase:
#             return product

#         cart, _ = Sell.get_user_cart(user=user)
#         if cart is None:
#             return product

#         is_owned_by_user = cart.products.filter(id=product.id).exists()
#         if is_owned_by_user:
#             raise serializers.ValidationError(
#                 "Ya obtuviste el producto o ya está en tu carrito."
#             )

#         if product.type != ProductTypes.PACKAGE:
#             return product

#         for item in product.items.all():
#             if not item.is_one_time_purchase:
#                 continue

#             is_owned_by_user = cart.products.filter(id=item.id).exists()
#             if is_owned_by_user:
#                 raise serializers.ValidationError(
#                     "Tu paquete incluye productos que ya compraste o está en tu carrito."
#                 )

#         return product


# class CartSerializer(serializers.ModelSerializer):
#     products = ProductSerializer(many=True, read_only=True)

#     class Meta:
#         model = Sell
#         fields = (
#             "products",
#             "status",
#             "payment_image",
#             "total_cost",
#             "on_cart_at",
#             "on_pending_at",
#             "paid_at",
#         )


# class UserProductBulkCreateSerializer(serializers.Serializer):
#     products = serializers.ListField(
#         child=serializers.PrimaryKeyRelatedField(
#             queryset=Product.objects.all()
#         ),
#         allow_empty=False,
#     )
#     first_name = serializers.CharField(max_length=255, allow_blank=False)
#     last_name = serializers.CharField(max_length=255, allow_blank=False)
#     email = serializers.EmailField(max_length=255, allow_blank=False)
#     token_id = serializers.CharField(max_length=25, allow_blank=False)

#     def validate_products(self, products):
#         user = self.context["request"].user

#         for product in products:
#             UserProduct.validate_product_purchase(user, product)

#         return products

#     def create(self, validated_data):
#         user = self.context["request"].user
#         user_name = validated_data["first_name"]
#         user_last_name = validated_data["last_name"]
#         user_email = validated_data["email"]
#         token_id = validated_data["token_id"]

#         products = validated_data["products"]
#         user_products = []

#         for product in products:
#             if product.type == ProductTypes.PACKAGE:
#                 # If the product is a package, add its items instead
#                 package_items = product.items.all()
#                 user_products.extend(
#                     [
#                         UserProduct(user=user, product=item)
#                         for item in package_items
#                     ]
#                 )
#             else:
#                 # Add non-package products directly
#                 user_products.append(UserProduct(user=user, product=product))

#         try:
#             with transaction.atomic():
#                 # Bulk create UserProduct entries
#                 UserProduct.objects.bulk_create(user_products)

#                 # Obteniendo precio total
#                 total_cost = Decimal("0.00")
#                 for prod in products:
#                     total_cost += prod.price

#                 # Create Sell instance and link products
#                 sell = Sell.objects.create(
#                     user=user,
#                     paid_at=timezone.now(),
#                     total_cost=total_cost,
#                     user_name=user_name,
#                     user_last_name=user_last_name,
#                     user_email=user_email,
#                 )
#                 sell.products.add(*products)

#                 # generate the pdf for the receipt
#                 receipt_data = sell.to_receipt_json
#                 html_string = render_to_string(
#                     "store/invoice_template.html", receipt_data
#                 )
#                 # Generate the PDF
#                 html = HTML(string=html_string)
#                 pdf_content = html.write_pdf()

#                 # Save the PDF in the receipt field
#                 pdf_filename = (
#                     f"receipt_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
#                 )
#                 sell.receipt.save(pdf_filename, ContentFile(pdf_content))

#                 culqi = Culqi()
#                 charge_data = culqi.create_charge(
#                     float(total_cost), user_email, token_id, "PEN"
#                 )

#                 sell.sell_identifier = charge_data["id"]
#                 sell.metadata = charge_data
#                 sell.save()

#                 logger.info(
#                     f"El usuario {user.username} realizó su compra de manera exitosa: ID de compra {sell.id}"
#                 )

#             return sell

#         except Exception as error:
#             error_msg = {
#                 "message": "Hubo un error al realizar la venta.",
#                 "error": str(error),
#             }
#             logger.error(
#                 f"El usuario {user.username} tuvo fallas en su compra a las {timezone.now()}. Error: {error}"
#             )
#             raise serializers.ValidationError(error_msg)


class ThreeDSParametersSerializer(serializers.Serializer):
    eci = serializers.CharField()
    xid = serializers.CharField()
    cavv = serializers.CharField()
    protocolVersion = serializers.CharField()
    directoryServerTransactionId = serializers.CharField()


class ChargePaymentSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    token = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField(min_length=5, max_length=15)
    device_id = serializers.CharField()
    parameters_3DS = ThreeDSParametersSerializer(
        required=False, allow_null=True
    )

    def validate_phone_number(self, value):
        if not re.match(r"^\d{5,15}$", value):
            raise serializers.ValidationError(
                _(
                    "Número de teléfono debe contener sólo dígitos y ser entre 5 y 15 caracteres de largo."
                )
            )
        return value


class SellSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Sell
        fields = ["products", "total_cost", "paid_at"]


class CreateSellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sell
        fields = [
            "id",
            "user_name",
            "user_last_name",
            "user_email",
            "user_phone_number",
            "products",
            "total_cost",
            "order_id",
        ]
        read_only_fields = ["order_id"]

    def validate_user_phone_number(self, value):
        if not re.match(r"^\d{5,15}$", value):
            raise serializers.ValidationError(
                _(
                    "Número de teléfono debe contener sólo dígitos y ser entre 5 y 15 caracteres de largo."
                )
            )
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        products = validated_data.pop("products", [])

        total_cost = Decimal("0.00")
        for prod in products:
            total_cost += prod.price

        sell = Sell.objects.create(
            user=user, total_cost=total_cost, **validated_data
        )
        sell.products.add(*products)
        sell.save()

        culqi = Culqi()
        order_data = culqi.create_order(sell)
        error = order_data.get("error", None)
        if error:
            sell.order_data = order_data
            sell.save()
            raise serializers.ValidationError(error)

        sell.order_id = order_data.get("id")
        sell.order_data = order_data
        sell.save()

        return sell


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = "__all__"
        read_only_fields = ["claim_number", "claim_file", "date"]

    def validate(self, data):
        """Custom validation for claim data."""
        if data.get("is_minor") and not data.get("proxy_name"):
            raise serializers.ValidationError(
                {
                    "proxy_name": "Proxy name is required if the claimant is a minor."
                }
            )
        return data

    def create(self, validated_data):
        try:
            with transaction.atomic():
                claim = Claim.objects.create(**validated_data)

                # generate the pdf for the receipt
                claim_data = claim.form_data
                html_string = render_to_string(
                    "store/form_lreclamaciones.html", claim_data
                )
                # Generate the PDF
                html = HTML(string=html_string)
                pdf_content = html.write_pdf()

                # Save the PDF in the receipt field
                pdf_filename = (
                    f"claim_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                )
                claim.claim_file.save(pdf_filename, ContentFile(pdf_content))

                logger.info(
                    f"El usuario '{claim.name}' realizó realizó su reclamos con ID '{claim.id}'"
                )

            return claim

        except Exception as error:
            error_msg = {
                "message": "Hubo un error al registrar datos en el libro de reclamaciones virtual.",
                "error": str(error),
            }
            logger.error(
                f"El usuario {validated_data['name']} tuvo fallas en su reclamación a las {timezone.now()}"
            )
            raise serializers.ValidationError(error_msg)
