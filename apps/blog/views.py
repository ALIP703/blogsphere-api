from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Exists, OuterRef
from django.utils import timezone
from rest_framework import status
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


@api_view(["GET"])
def likeAPost(request, pk):
    try:
        if not request.user.is_authenticated:
            return Response(
                {
                    "status": status.HTTP_403_FORBIDDEN,
                    "message": "You are not allowed to access this resource.",
                    "data": [],
                }
            )
        # Check if the post exists
        post = Posts.objects.get(pk=pk)

        # Check if the user has already liked the post
        like = Likes.objects.filter(author=request.user, post=post).first()

        if like:
            # User has already liked the post, so remove the like
            like.delete()
            message = "Blog disliked successfully"
        else:
            # User has not liked the post, so add a new like
            Likes.objects.create(author=request.user, post=post)
            message = "Blog liked successfully"

        response = {
            "message": message,
            "status": status.HTTP_200_OK,
        }
    except ObjectDoesNotExist:
        response = {
            "message": "Post not found",
            "status": status.HTTP_404_NOT_FOUND,
        }
    except Exception as e:
        response = {
            "message": str(e),
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

    return Response(response, status=response["status"])


@api_view(["GET"])
def likeAComment(request, pk):
    try:
        # Check if the post exists
        comment = Comments.objects.get(pk=pk)

        # Check if the user has already liked the post
        like = CommentLikes.objects.filter(author=request.user, comment=comment).first()

        if like:
            # User has already liked the post, so remove the like
            like.delete()
            message = "Comment disliked successfully"
        else:
            # User has not liked the post, so add a new like
            CommentLikes.objects.create(author=request.user, comment=comment)
            message = "Comment liked successfully"

        response = {
            "message": message,
            "status": status.HTTP_200_OK,
        }
    except ObjectDoesNotExist:
        response = {
            "message": "Comment not found",
            "status": status.HTTP_404_NOT_FOUND,
        }
    except Exception as e:
        response = {
            "message": str(e),
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

    return Response(response, status=response["status"])
