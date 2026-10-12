from django.urls import path

from kanban_app.api.views import (
    AssignedToMeView,
    BoardDetailView,
    BoardListCreateView,
    ReviewingView,
    TaskCreateView,
)

urlpatterns = [
    path("boards/", BoardListCreateView.as_view(), name="board-list"),
    path("boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),
    path("tasks/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/assigned-to-me/", AssignedToMeView.as_view(),
         name="tasks-assigned"),
    path("tasks/reviewing/", ReviewingView.as_view(), name="tasks-reviewing"),
]
