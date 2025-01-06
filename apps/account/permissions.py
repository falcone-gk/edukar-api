from rest_framework.permissions import BasePermission

from .models import UserProduct


class IsProductOwner(BasePermission):
    """
    Custom permission to check if the user owns the product.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user has access to the specific product
        return UserProduct.objects.filter(
            user=request.user, product=obj
        ).exists()
