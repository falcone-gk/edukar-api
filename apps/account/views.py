from account.models import UserProduct
from account.serializers import (
    UpdateUserInfoSerializer,
    UpdateUserProfileSerializer,
)
from core.paginators import CustomPagination
from djoser.permissions import CurrentUserOrAdminOrReadOnly
from forum.models import Post
from forum.permissions import IsAuthorOrReadOnly
from forum.serializers import PostResumeSerializer
from rest_framework import generics, mixins, status, views, viewsets
from rest_framework.authtoken.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from store.models import Category, Sell
from store.serializers import PrivateProductSerializer, SellSerializer


# Create your views here.
class UserByTokenAPIView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        return Response(
            {
                "token": user.auth_token.key,
                "username": user.username,
                "email": user.email,
                "picture": user.profile.get().picture.url,
                "has_notification": user.notif.filter(is_read=False).exists(),
            }
        )


class LogoutAPIView(views.APIView):
    def post(self, request):
        if request.user.is_authenticated:
            request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OwnerPostAPIView(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PostResumeSerializer
    permission_classes = (
        IsAuthenticated,
        IsAuthorOrReadOnly,
    )
    pagination_class = CustomPagination
    lookup_field = "slug"

    def get_queryset(self):
        current_user = self.request.user
        return Post.objects.filter(author=current_user).order_by("-date")


class UpdateUserAPIView(generics.UpdateAPIView):
    serializer_class = UpdateUserInfoSerializer
    permission_classes = (CurrentUserOrAdminOrReadOnly,)

    def get_instance(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return super().update(request, *args, **kwargs)


class UpdateUserProfileAPIView(generics.UpdateAPIView):
    serializer_class = UpdateUserProfileSerializer
    permission_classes = (CurrentUserOrAdminOrReadOnly,)

    def get_instance(self):
        return self.request.user.profile.get()

    def update(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        response = super().update(request, *args, **kwargs)

        if response.status_code == 200:
            response.data["picture"] = request.user.profile.get().picture.url

        return response


# class UploadUserImageAPIView(APIView):
#
#     serializer_class = UploadUserImageSerializer
#     permission_classes = (IsAuthenticated,)
#
#     def post(self, request, *args, **kwargs):
#
#         context = { 'request': request }
#         serializer = UploadUserImageSerializer(data=request.data, context=context)
#         serializer.is_valid(raise_exception=True)
#         new_instance = serializer.save()
#         instance_serializer = UrlUserImageSerializer(new_instance)
#         return Response(instance_serializer.data, status=status.HTTP_201_CREATED)


# TODO: Add test for this endpoint
class UserProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the category with the name "Solucionario"
        category = Category.get_solutionary_category()

        # Filter UserProduct by the requesting user and the category
        user_products = (
            UserProduct.objects.filter(
                user=request.user, product__category=category
            )
            .select_related("product")
            .order_by("-id")
        )

        # Extract the products
        products = [user_product.product for user_product in user_products]

        # Serialize the products
        serializer = PrivateProductSerializer(
            products, many=True, context={"request": request}
        )

        return Response(serializer.data)


# TODO: Add test for this endpoint
class UserPurchasesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filter the purchases for the authenticated user
        purchases = Sell.objects.filter(user=request.user).prefetch_related(
            "products"
        )

        # Serialize the purchase data
        serializer = SellSerializer(purchases, many=True)

        return Response(serializer.data)
