from rest_framework import serializers

from .models import Comments, Posts, Tags, UploadedFile


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
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
