from rest_framework import serializers

from .models import CommentLikes, Comments, Likes, Posts, Saved, User


class blogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = "__all__"
