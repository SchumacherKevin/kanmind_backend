from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    """Validates registration data (fullname, email, password, repeated_password)."""
    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """Check if the email is already in use."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, attrs):
        """Check if the passwords match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        """Create a new user; the email doubles as the username."""
        first_name, _, last_name = validated_data['fullname'].partition(' ')
        return User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
        )


class LoginSerializer(serializers.Serializer):
    """Validates login credentials (email + password)."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the user and attach it to the validated data."""
        user = authenticate(
            username=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        attrs['user'] = user
        return attrs
