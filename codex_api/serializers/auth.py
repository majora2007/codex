"""Codex Auth Serializers."""

from django.contrib.auth.models import User
from rest_framework.fields import BooleanField
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer


class UserSerializer(ModelSerializer):
    """Serialize User model for UI."""

    class Meta:
        """Model spec."""

        model = User
        fields = ("pk", "username", "is_staff")
        read_only_fields = fields


class UserCreateSerializer(ModelSerializer):
    """Serialize registration input for creating users."""

    class Meta:
        """Model spec."""

        model = User
        fields = ("username", "password")
        extra_kwargs = {"password": {"write_only": True}}


class UserLoginSerializer(UserCreateSerializer):
    """Serialize user login input."""

    # specificy this so it doesn't trigger the username unique constraint.
    username = CharField(min_length=2)


class RegistrationEnabledSerializer(Serializer):
    """Serialize one admin flag."""

    enableRegistration = BooleanField(read_only=True)  # noqa: N815
