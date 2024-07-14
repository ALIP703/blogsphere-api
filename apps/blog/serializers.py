from rest_framework import serializers

from .models import CommentLikes, Comments, Likes, Posts, Saved, User


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = "__all__"
