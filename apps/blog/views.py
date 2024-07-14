# from datetime import timedelta

# from django.http import JsonResponse
# from django.shortcuts import render
# from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import CommentLikes, Comments, Likes, Posts, Saved, User
from .serializers import blogSerializer


# Create your api views here.
@api_view(["GET"])
def blogs(request):
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
