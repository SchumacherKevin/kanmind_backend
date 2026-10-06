from os import path

from kanban_app.api.views import BoardListCreateView


urlpatterurlpatterns = [
    path("boards/", BoardListCreateView.as_view(), name="board-list"),
]
