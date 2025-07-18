import logging

from account.models import UserProduct
from account.permissions import IsProductOwner
from core.paginators import CustomPagination
from django.http import Http404
from django.utils.translation import gettext as _
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    GenericViewSet,
    ReadOnlyModelViewSet,
)
from store.models import Category, Product, ProductComment, Sell
from store.serializers import (
    CategorySerializer,
    ChargePaymentSerializer,
    ClaimSerializer,
    CreateSellSerializer,
    ProductCreateCommentSerializer,
    ProductSerializer,
)
from store.tasks import send_user_claim

from helpers.choices import ProductTypes, SellStatus
from helpers.responses import get_streaming_response
from utils.products import assign_product_to_user
from utils.services.cloudflare import Cloudflare
from utils.services.culqi import Culqi

# Create your views here.


logger = logging.getLogger(__name__)


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
        queryset = Product.objects.filter(show=True).order_by("-id")
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

    # TODO: Hacer tests de este endpoint
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def comment(self, request, slug=None):
        """Create a comment for a product identified by slug"""
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductCreateCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ProductComment.objects.create(
            user=request.user,
            product=product,
            comment=serializer.validated_data["comment"],
        )
        return Response(
            {"detail": "Comment created successfully"},
            status=status.HTTP_201_CREATED,
        )


class CheckProductPurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    # TODO: Agregar tests de endpoint
    def post(self, request, format=None):
        user = request.user
        product_identifier = request.data.get("identifier")

        if not product_identifier:
            return Response(
                {"error": "El campo 'identifier' es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(Product, identifier=product_identifier)

        try:
            UserProduct.validate_product_purchase(user, product)
        except ValidationError as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "El producto puede ser añadido al carrito."},
            status=status.HTTP_200_OK,
        )


class StartSellView(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateSellSerializer
    queryset = Sell.objects.all()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=["POST"])
    def pay(self, request, pk=None):
        sell: Sell = self.get_object()

        if sell.status == SellStatus.FINISHED:
            return Response(
                {"error": _("Venta ya finalizada.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate request data with serializer
        serializer = ChargePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        culqi = Culqi()
        response = culqi.create_charge(sell, **validated_data)
        status_code = response.status_code

        if status_code == 201:
            sell_data = response.json()
            sell.mark_as_paid(sell_data)

            # Register user products
            assign_product_to_user(sell)

            logger.info(
                f"El usuario {sell.user.username} realizó su compra de manera exitosa: "
                f"ID de compra {sell.id}"
            )
        elif status_code == 200:
            sell.status = SellStatus.PENDING
            sell.metadata = response.json()
            sell.save()
            logger.info(
                f"El usuario {sell.user.username} necesita autentificación con 3DS: "
                f"ID de compra {sell.id}"
            )
        else:
            sell.status = SellStatus.FAILED
            sell.metadata = response.json()
            sell.save()
            logger.error(
                f"El usuario {sell.user.username} falló su compra: "
                f"Error de compra {sell.id}"
            )

        return Response(response.json(), status=status_code)

    @action(
        detail=True,
        methods=["POST"],
        url_name="set-error",
        url_path="set-error",
    )
    def set_error(self, request, pk=None):
        error = request.data
        sell = self.get_object()
        sell.status = SellStatus.FAILED
        sell.metadata = error
        sell.save()
        return Response(status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["GET"],
        url_name="consult-order",
        url_path="consult-order",
    )
    def consult_order(self, request, pk=None):
        sell: Sell = self.get_object()
        culqi = Culqi()
        data = culqi.consult_order(sell.order_id)
        error = data.get("error", None)

        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        current_order_state = data.get("state")

        message = {"state": current_order_state}
        return Response(message, status=status.HTTP_200_OK)


# TODO: Se descomentará cuando se habilite pasarela
# class UserProductBulkCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         serializer = UserProductBulkCreateSerializer(
#             data=request.data, context={"request": request}
#         )
#         serializer.is_valid(raise_exception=True)
#         sell = serializer.save()

#         send_sell_receipt_to_user_email(sell)

#         return Response(
#             {"receipt_url": sell.receipt.url},
#             status=status.HTTP_201_CREATED,
#         )


# TODO: Add test for this view
class DownloadProductDocumentView(APIView):
    permission_classes = (IsProductOwner,)

    def get_object(self, slug):
        try:
            return Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        user = self.request.user
        document = self.get_object(slug)
        doc_key = document.source
        cf = Cloudflare(user)

        try:
            file_stream = cf.get_document(doc_key)
            # Return the file as a downloadable response
            return get_streaming_response(file_stream, slug, "pdf")
        except Exception as error:
            error_msg = {
                "message": "No se pudo descargar el documento. Avisar a soporte sobre el problema",
                "error": str(error),
            }
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)


# TODO: Add tests for this endpoint
class ClaimCreateView(APIView):
    def post(self, request):
        serializer = ClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        claim = serializer.save()
        send_user_claim(claim)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# def view_invoice(request, sell_id):
#     """
#     Vista para mostrar el HTML del recibo de una venta.
#     :param request: HttpRequest
#     :param sell_id: ID de la venta
#     :return: HttpResponse con el HTML renderizado
#     """
#     sell = get_object_or_404(Sell, id=sell_id)
#     receipt_data = sell.to_receipt_json
#     return render(request, "store/invoice_template.html", receipt_data)


# Este es un endpoint temporal en el caso que no se haya enviado correctamente el correo
# class InvoiceSendAPIView(APIView):
#     """
#     APIView para generar un PDF del recibo y enviarlo por correo electrónico.
#     """

#     def get(self, request, sell_id):
#         """
#         Genera el PDF del recibo y lo envía por correo.
#         :param request: HttpRequest
#         :param sell_id: ID de la venta
#         :return: Response con el resultado de la operación
#         """
#         sell = get_object_or_404(Sell, id=sell_id)

#         # Verifica si la venta está marcada como pagada
#         if sell.status != SellStatus.FINISHED:
#             return Response(
#                 {"error": "La venta no está marcada como pagada."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Genera el PDF del recibo (esto ya se hace en el método `generate_receipt` del modelo)
#         sell.generate_receipt()

#         # Envía el correo electrónico con el PDF adjunto
#         send_sell_receipt_to_user_email(sell)
#         logger.info(
#             f"Se ha enviado el correo al usuario {sell.user.username}, con ID de compra '{sell.id}'"
#         )

#         return Response(
#             {"message": "El recibo ha sido generado y enviado por correo."},
#             status=status.HTTP_200_OK,
#         )
