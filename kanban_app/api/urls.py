from django.urls import path

from kanban_app.api.views import (
    AssignedToMeView,
    BoardDetailView,
    BoardListCreateView,
    CommentDeleteView,
    CommentListCreateView,
    ReviewingView,
    TaskCreateView,
    TaskDetailView,
)

urlpatterns = [
    path("boards/", BoardListCreateView.as_view(), name="board-list"),
    path("boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),
    path("tasks/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/assigned-to-me/", AssignedToMeView.as_view(),
         name="tasks-assigned"),
    path("tasks/reviewing/", ReviewingView.as_view(), name="tasks-reviewing"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path(
        "tasks/<int:task_id>/comments/",
        CommentListCreateView.as_view(),
        name="comment-list",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        CommentDeleteView.as_view(),
        name="comment-delete",
    ),
]
