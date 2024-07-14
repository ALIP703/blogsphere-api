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

        # Determine the display format of the post's creation date
        today = timezone.now().date()
        if post.created_at.date() == today:
            created_at_display = "Today"
        elif post.created_at.date() == today - timedelta(days=1):
            created_at_display = "Yesterday"
        else:
            created_at_display = post.created_at

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
        # Build the context
        context = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": created_at_display,
            "user": request.user.username if request.user.is_authenticated else None,
            "liked": liked,
            "saved": saved,
        }

        # Create the response dictionary
        response = {
            "data": context,
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
