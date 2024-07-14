from datetime import timedelta

from django.db.models import Exists, OuterRef
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import CommentLikes, Comments, Likes, Posts, Saved, User
from .serializers import BlogSerializer, CommentSerializer


# Create your api views here.
@api_view(["GET"])
def getAllBlogs(request):
    try:
        posts = Posts.objects.all()
        serializer = BlogSerializer(posts, many=True)
        response = {
            "data": serializer.data,
            "message": "successfully retrieved all blogs",
            "status": 200,
        }

    except Exception as e:
        response = {
            "data": [],
            "message": f"An error occurred: {str(e)}",
            "status": 500,
        }

    # Return the JSON response with posts and their associated data
    return Response(response)


@api_view(["POST"])
def createBlog(request):
    try:
        if not request.user.is_authenticated:
            return Response(
                {
                    "status": 403,
                    "message": "You are not allowed to access this resource.",
                    "data": [],
                }
            )
        # Make a copy of request.data and add the author field
        blog_data = request.data.copy()
        blog_data["author"] = request.user.id

        serializer = BlogSerializer(data=blog_data)
        if serializer.is_valid():
            serializer.save()
        response = {
            "data": serializer.data,
            "message": "successfully created blog",
            "status": 500,
        }
    except Exception as e:
        response = {
            "data": [],
            "message": f"An error occurred: {str(e)}",
            "status": 500,
        }
    return Response(response)


@api_view(["GET"])
def getABlog(request, pk):
    try:
        post = Posts.objects.get(pk=pk)
        serializer = BlogSerializer(post)
        # Check if the current user has liked or saved this post
        liked = (
            Likes.objects.filter(post=post, author=request.user).exists()
            if request.user.is_authenticated
            else False
        )
        saved = (
            Saved.objects.filter(post=post, author=request.user).exists()
            if request.user.is_authenticated
            else False
        )
        # Create a copy of the serialized data and add the 'saved' and 'liked' fields
        post_data = serializer.data.copy()
        post_data["liked"] = liked
        post_data["saved"] = saved
        # Create the response dictionary
        response = {
            "data": post_data,
            "message": "successfully retrieved A blog post",
            "status": 200,
        }

    except Exception as e:
        response = {
            "data": None,
            "message": f"An error occurred: {str(e)}",
            "status": 500,
        }

    return Response(response)


@api_view(["GET"])
def getAllCommentsByPostId(request, pk):
    try:
        comments = Comments.objects.filter(post=pk, parent=None)

        if not comments.exists():
            response = {
                "data": None,
                "message": "No comments found for this post.",
                "status": 200,
            }
            return Response(response)

        # Serialize the annotated comments
        serializer = CommentSerializer(comments, many=True)
        for comment in serializer.data:
            liked = (
                CommentLikes.objects.filter(
                    comment=comment["id"], author=request.user
                ).exists()
                if request.user.is_authenticated
                else False
            )
            comment["liked"] = liked
        # Create the response dictionary
        response = {
            "data": serializer.data,
            "message": "Successfully retrieved the comments",
            "status": 200,
        }
    except Exception as e:
        response = {
            "data": None,
            "message": f"An error occurred: {str(e)}",
            "status": 500,
        }

    return Response(response)


@api_view(["GET"])
def getAllReplyByCommentId(request, pk):
    try:
        comments = Comments.objects.filter(parent=pk)
        if not comments.exists():
            response = {
                "data": None,
                "message": "No reply found for this comment.",
                "status": 200,
            }
            return Response(response)

        # Serialize the annotated comments
        serializer = CommentSerializer(comments, many=True)
        for comment in serializer.data:
            liked = (
                CommentLikes.objects.filter(
                    comment=comment["id"], author=request.user
                ).exists()
                if request.user.is_authenticated
                else False
            )
            comment["liked"] = liked
        # Create the response dictionary
        response = {
            "data": serializer.data,
            "message": "Successfully retrieved the reply comments",
            "status": 200,
        }
    except Exception as e:
        response = {
            "data": None,
            "message": f"An error occurred: {str(e)}",
            "status": 500,
        }

    return Response(response)
