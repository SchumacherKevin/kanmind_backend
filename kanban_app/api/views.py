from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from kanban_app.api.permissions import (
    IsBoardMemberOrOwner,
    IsCommentAuthor,
    IsTaskBoardMember,
    IsTaskBoardMemberByUrl,
    IsTaskCreatorOrBoardOwner,
)
from kanban_app.api.serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    TaskSerializer,
    TaskUpdateSerializer,
)
from kanban_app.models import Board, Comment, Priority, Status, Task


def tasks_with_details():
    """Return tasks with assignee, reviewer and comment count preloaded."""
    return Task.objects.select_related("assignee", "reviewer").annotate(
        comments_count=Count("comments")
    )


def boards_with_counts():
    """Return boards annotated with member and task counters."""
    return Board.objects.annotate(
        member_count=Count("members", distinct=True),
        ticket_count=Count("tasks", distinct=True),
        tasks_to_do_count=Count(
            "tasks", filter=Q(tasks__status=Status.TO_DO), distinct=True
        ),
        tasks_high_prio_count=Count(
            "tasks", filter=Q(tasks__priority=Priority.HIGH), distinct=True
        ),
    )


class BoardListCreateView(generics.ListCreateAPIView):
    """List the user's boards or create a new one."""

    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return boards where the user is the owner or a member."""
        user = self.request.user
        board_ids = Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).values("pk")
        return boards_with_counts().filter(pk__in=board_ids)

    def perform_create(self, serializer):
        """Save with the user as owner and reload it with its counters."""
        board = serializer.save(owner=self.request.user)
        serializer.instance = boards_with_counts().get(pk=board.pk)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a single board."""

    queryset = Board.objects.prefetch_related(
        "members", Prefetch("tasks", queryset=tasks_with_details())
    )
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]
    http_method_names = ["get", "patch", "delete"]

    def get_serializer_class(self):
        """Use the update serializer for PATCH, otherwise the detail one."""
        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer


class TaskCreateView(generics.CreateAPIView):
    """Create a task on a board the user belongs to."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def create(self, request, *args, **kwargs):
        """Check board existence and membership before validating."""
        board = get_object_or_404(Board, pk=request.data.get("board"))
        self.check_object_permissions(request, board)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Save with the user as creator and reload it with its details."""
        task = serializer.save(created_by=self.request.user)
        serializer.instance = tasks_with_details().get(pk=task.pk)


class AssignedToMeView(generics.ListAPIView):
    """List tasks assigned to the authenticated user."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tasks assigned to the authenticated user."""
        user = self.request.user
        return tasks_with_details().filter(assignee=user)


class ReviewingView(generics.ListAPIView):
    """List tasks where the authenticated user is the reviewer."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tasks where the authenticated user is the reviewer."""
        user = self.request.user
        return tasks_with_details().filter(reviewer=user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Update or delete a single task."""

    queryset = tasks_with_details()
    serializer_class = TaskUpdateSerializer
    http_method_names = ["patch", "delete"]

    def get_permissions(self):
        """Creator or board owner may delete; board members may update."""
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsTaskBoardMember()]


class CommentListCreateView(generics.ListCreateAPIView):
    """List or create comments on a task."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberByUrl]

    def get_queryset(self):
        """Return the comments of the task from the URL."""
        return Comment.objects.filter(
            task_id=self.kwargs["task_id"]
        ).select_related("author")

    def perform_create(self, serializer):
        """Attach the task from the URL and the requesting user."""
        serializer.save(
            task_id=self.kwargs["task_id"], author=self.request.user
        )


class CommentDeleteView(generics.DestroyAPIView):
    """Delete a comment; only its author may do so."""

    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        """Only consider comments that belong to the task from the URL."""
        return Comment.objects.filter(
            task_id=self.kwargs["task_id"]
        )
