from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    EmailQuerySerializer,
    LoginSerializer,
    RegistrationSerializer,
    UserSerializer,
)


def build_auth_response(user):
    """Build a response containing the auth token and user data."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "fullname": user.get_full_name(),
        "email": user.email,
        "user_id": user.id,
    }


class RegistrationView(APIView):
    """Register a new user and return an auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Create the user and respond with token and user data."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(build_auth_response(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Log in an existing user and return an auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate the credentials and respond with token and user data."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response(build_auth_response(user), status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    """Return the user for the given email or 404."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Validate the email query parameter and return the user data."""
        serializer = EmailQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, email=serializer.validated_data['email'])
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
