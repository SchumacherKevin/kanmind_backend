from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from kanban_app.api.permissions import IsBoardMemberOrOwner
from kanban_app.api.serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
)
from kanban_app.models import Board


class BoardListCreateView(generics.ListCreateAPIView):
    """List the user's boards or create a new one."""

    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return boards where the user is the owner or a member."""
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        """Set the owner of the new board to the authenticated user."""
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a single board."""

    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]
    http_method_names = ["get", "patch", "delete"]

    def get_serializer_class(self):
        """Use the update serializer for PATCH, otherwise the detail one."""
        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer
