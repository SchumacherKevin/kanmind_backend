from django.contrib.auth.models import User
from rest_framework import serializers

from kanban_app.models import Board, Priority, Status
from auth_app.api.serializers import UserSerializer


class BoardListSerializer(serializers.ModelSerializer):
    """Serialize boards for the list view and board creation."""

    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True
    )
    owner_id = serializers.ReadOnlyField(source="owner.id")
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id", "title", "members", "member_count", "ticket_count",
            "tasks_to_do_count", "tasks_high_prio_count", "owner_id",
        ]

    def get_member_count(self, obj):
        """Return the number of board members."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the total number of tasks on the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks with status 'to-do'."""
        return obj.tasks.filter(status=Status.TO_DO).count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of tasks with priority 'high'."""
        return obj.tasks.filter(priority=Priority.HIGH).count()


class TaskNestedSerializer(serializers.ModelSerializer):
    """Serialize tasks for nested representation in board details."""

    id = serializers.ReadOnlyField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000, allow_blank=True)
    status = serializers.ChoiceField(choices=Status.choices)
    priority = serializers.ChoiceField(choices=Priority.choices)
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    due_date = serializers.DateField(allow_null=True, required=False)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Board.tasks.through
        fields = ["id", "title", "description", "status", "priority",
                  "assignee", "reviewer", "due_date", "comments_count"]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serialize boards for the detail view, including members and tasks."""

    id = serializers.ReadOnlyField()
    title = serializers.CharField(max_length=255)
    owner_id = serializers.ReadOnlyField(source="owner.id")
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serialize boards for updates, allowing title and members to be changed."""

    id = serializers.ReadOnlyField()
    title = serializers.CharField(max_length=255)
    owner_data = UserSerializer(source="owner", read_only=True)
    member_data = UserSerializer(source="members", many=True, read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True
    )

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "member_data", "members"]
