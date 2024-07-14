from datetime import timedelta

from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import CommentLikes, Comments, Likes, Posts, Saved, User
from .serializers import blogSerializer


# Create your api views here.
@api_view(["GET"])
def getAllBlogs(request):
    try:
        posts = Posts.objects.all()
        serializer = blogSerializer(posts, many=True)
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

        serializer = blogSerializer(data=blog_data)
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
        serializer = blogSerializer(post)
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
