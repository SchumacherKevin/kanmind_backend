from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):
    """Allow board members and the owner; only the owner may delete."""

    def has_object_permission(self, request, view, obj):
        """Check access to a single board."""
        is_owner = obj.owner == request.user
        if request.method == "DELETE":
            return is_owner
        return is_owner or obj.members.filter(id=request.user.id).exists()
