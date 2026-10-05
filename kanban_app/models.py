from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    """A kanban board owned by one user and shared with members."""

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_boards"
    )
    members = models.ManyToManyField(User, related_name="boards", blank=True)

    class Meta:
        verbose_name = "Board"
        verbose_name_plural = "Boards"
        ordering = ["id"]

    def __str__(self):
        return self.title


class Status(models.TextChoices):
    TO_DO = "to-do", "To do"
    IN_PROGRESS = "in-progress", "In progress"
    REVIEW = "review", "Review"
    DONE = "done", "Done"


status = models.CharField(
    max_length=20, choices=Status.choices, default=Status.TO_DO)


class Priority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


priority = models.CharField(
    max_length=20, choices=Priority.choices, default=Priority.MEDIUM)


class Task(models.Model):
    """ A task that belongs to a board and can be assigned to users. """

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.TO_DO
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    assignee = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="review_tasks"
    )
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_tasks"
    )
