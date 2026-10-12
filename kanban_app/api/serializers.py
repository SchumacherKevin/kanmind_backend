from django.contrib.auth.models import User
from rest_framework import serializers

from auth_app.api.serializers import UserSerializer
from kanban_app.api.permissions import is_board_user
from kanban_app.models import Board, Comment, Priority, Status, Task


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

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "priority",
            "assignee", "reviewer", "due_date", "comments_count",
        ]

    def get_comments_count(self, obj):
        """Return the number of comments on the task."""
        return obj.comments.count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serialize boards for the detail view, including members and tasks."""

    owner_id = serializers.ReadOnlyField(source="owner.id")
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serialize board updates of title and members."""

    owner_data = UserSerializer(source="owner", read_only=True)
    members_data = UserSerializer(source="members", many=True, read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True
    )

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data", "members"]


class TaskSerializer(TaskNestedSerializer):
    """Serialize tasks with board and writable assignee/reviewer ids."""

    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta(TaskNestedSerializer.Meta):
        fields = [
            "id", "board", "title", "description", "status", "priority",
            "assignee", "reviewer", "assignee_id", "reviewer_id",
            "due_date", "comments_count",
        ]

    def validate(self, attrs):
        """Ensure assignee and reviewer belong to the task's board."""
        board = attrs.get("board") or self.instance.board
        for field in ("assignee", "reviewer"):
            user = attrs.get(field)
            if user and not is_board_user(board, user):
                raise serializers.ValidationError(
                    {f"{field}_id": "User must be a member of the board."}
                )
        return attrs


class TaskUpdateSerializer(TaskSerializer):
    """Serialize task updates; the board may not be changed."""

    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all(), write_only=True, required=False
    )

    class Meta(TaskSerializer.Meta):
        fields = [
            "id", "board", "title", "description", "status", "priority",
            "assignee", "reviewer", "assignee_id", "reviewer_id", "due_date",
        ]

    def validate_board(self, value):
        """Reject any attempt to move the task to another board."""
        if value != self.instance.board:
            raise serializers.ValidationError(
                "Changing the board is not allowed.")
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Serialize comments with author and task information."""

    author = serializers.ReadOnlyField(source="author.get_full_name")

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]
