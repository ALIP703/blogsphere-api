from django.contrib.auth.models import User
from rest_framework import serializers

from apps.users.models import profile

from .models import Comments, Posts, Tags, UploadedFile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile
        fields = ["image", "bio"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)  # Nested serializer for profile

    class Meta:
        model = User
        fields = ["id", "username", "profile"]


# Serializer for the Tags model
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = "__all__"


# Serializer for the Posts model
class BlogSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)  # Nested serializer for author
    tags = TagSerializer(many=True, read_only=True)  # Nested serializer for tags

    class Meta:
        model = Posts
        fields = [
            "id",
            "title",
            "subtitle",
            "content",
            "thumbnail",
            "created_at",
            "updated_at",
            "author",  # Include nested author
            "tags",  # Include nested tags
        ]


class BlogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)  # Nested serializer for author

    class Meta:
        model = Comments
        fields = [
            "id",
            "message",
            "created_at",
            "updated_at",
            "author",
            "post",
            "parent",
        ]


class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comments
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = "__all__"


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = "__all__"
