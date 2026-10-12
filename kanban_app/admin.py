from django.contrib import admin

from kanban_app.models import Board, Comment, Task


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin interface for the Board model."""

    list_display = ('id', 'title', 'owner')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for the Task model."""

    list_display = ('id', 'title', 'board', 'status', 'priority')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for the Comment model."""

    list_display = ('id', 'task', 'author', 'created_at')
