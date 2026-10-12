from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from kanban_app.models import Task


def is_board_user(board, user):
    """Return True if the user owns or is a member of the board."""
    return (
        board.owner == user
        or board.members.filter(id=user.id).exists()
    )


class IsBoardMemberOrOwner(BasePermission):
    """Allow board members and the owner; only the owner may delete."""

    def has_object_permission(self, request, view, obj):
        """Check access to a single board."""
        is_owner = obj.owner == request.user
        if request.method == "DELETE":
            return is_owner
        return is_board_user(obj, request.user)


class IsTaskBoardMember(BasePermission):
    """Allow access to tasks if the user is a member of the task's board."""

    def has_object_permission(self, request, view, obj):
        """Check access to a single task."""
        return is_board_user(obj.board, request.user)


class IsTaskCreatorOrBoardOwner(BasePermission):
    """Allow access to tasks if the user is the creator or board owner."""

    def has_object_permission(self, request, view, obj):
        """Check access to a single task."""
        return (
            obj.created_by == request.user
            or obj.board.owner == request.user
        )


class IsTaskBoardMemberByUrl(BasePermission):
    """Allow access if the user belongs to the board of the URL's task."""

    def has_permission(self, request, view):
        """Look up the task from the URL and check board membership."""
        task = get_object_or_404(Task, pk=view.kwargs["task_id"])
        return is_board_user(task.board, request.user)


class IsCommentAuthor(BasePermission):
    """Allow access to comments if the user is the author."""

    def has_object_permission(self, request, view, obj):
        """Check access to a single comment."""
        return obj.author == request.user
