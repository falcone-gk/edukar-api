from rest_framework import permissions

class isOwnNotification(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):

        # Instance must have an attribute named `owner`.
        return obj.user == request.user