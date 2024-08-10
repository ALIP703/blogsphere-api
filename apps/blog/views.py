import json
from datetime import datetime, timedelta

import pytz
from dateutil import parser
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Exists, OuterRef
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CommentLikes, Comments, Likes, Posts, Saved, Tags, UploadedFile
from .serializers import (
    BlogCreateSerializer,
    BlogSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    TagSerializer,
    UploadedFileSerializer,
)


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


def format_date_time(date_time_str):
    # Define the IST timezone
    ist = pytz.timezone("Asia/Kolkata")

    # Parse the created_at string to a datetime object and convert to IST
    date_time = parser.parse(date_time_str)
    date_time_ist = date_time.astimezone(ist)

    # Get today's date in IST
    today_ist = datetime.now(ist).date()

    # Check if created_at is today
    if date_time_ist.date() == today_ist:
        # Format to show only time if the date is today
        return date_time_ist.strftime("%I:%M %p")
    else:
        # Format to show full date if the date is not today
        return date_time_ist.strftime("%B %d, %Y")


# Create your api views here.
@api_view(["GET"])
def getAllBlogs(request):
    try:
        # Get all posts
        posts = Posts.objects.all()

        # Create an instance of the pagination class
        paginator = CustomLimitOffsetPagination()
        # Paginate the queryset
        paginated_posts = paginator.paginate_queryset(posts, request)

        # Serialize the paginated queryset
        serializer = BlogSerializer(paginated_posts, many=True)

        # Create the response with pagination data
        paginated_response = paginator.get_paginated_response(serializer.data)
        data = paginated_response.data

        response = {
            "data": data,
            "message": "Successfully retrieved all blogs",
            "status": status.HTTP_200_OK,
        }
        return Response(response, status=response["status"])

    except Exception as e:
        response = {
            "data": [],
            "message": f"An error occurred: {str(e)}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        return Response(response, status=response["status"])


@api_view(["GET"])
def getAllBlogsByUserId(request, pk):
    try:
        user = User.objects.get(pk=pk)
        # Get all posts of this user
        posts = Posts.objects.filter(author=user)

        # Create an instance of the pagination class
        paginator = CustomLimitOffsetPagination()
        # Paginate the queryset
        paginated_posts = paginator.paginate_queryset(posts, request)

        # Serialize the paginated queryset
        serializer = BlogSerializer(paginated_posts, many=True)

        # Create the response with pagination data
        paginated_response = paginator.get_paginated_response(serializer.data)
        data = paginated_response.data

        response = {
            "data": data,
            "message": "Successfully retrieved all blogs",
            "status": status.HTTP_200_OK,
        }
        return Response(response, status=response["status"])

    except Exception as e:
        response = {
            "data": [],
            "message": f"An error occurred: {str(e)}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        return Response(response, status=response["status"])


class FileUploadView(APIView):
    serializer_class = UploadedFileSerializer

    def post(self, request):
        if "file" not in request.FILES:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]

        # Save the file URL to the database if using a model
        # uploaded_file = UploadedFile.objects.create(data=file)

        # Serialize and return the response
        serializer = self.serializer_class(data={"file": file})
        if serializer.is_valid():
            # Uncomment if you are saving the file with a model
            # uploaded_file = serializer.save()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["POST"])
# def createBlog(request):
class CreateBlogView(APIView):
    serializer_class = BlogSerializer

    def post(self, request):
        try:
            if not request.user.is_authenticated:
                response = {
                    "status": status.HTTP_403_FORBIDDEN,
                    "message": "You are not allowed to access this resource.",
                    "data": [],
                }
                return Response(response, status=response["status"])
            # Make a copy of request.data and add the author field
            blog_data = request.data.copy()
            content = json.loads(blog_data["content"])
            title = None
            subtitle = None

            # Flag to indicate if the first heading has been found
            found_first_heading = False

            # Iterate through the list to find the first heading and next heading or paragraph
            for item in content:
                if not found_first_heading:
                    if item.get("type") == "heading":
                        # Extract text from the first heading
                        if item.get("content"):
                            title = item["content"][0].get("text")
                        found_first_heading = True
                else:
                    # After finding the first heading, look for the next heading or paragraph
                    if item.get("type") in ["heading", "paragraph"]:
                        if item.get("content"):
                            subtitle = item["content"][0].get("text")
                        break
            blog_data["title"] = title
            blog_data["subtitle"] = subtitle
            blog_data["author"] = request.user.id
            serializer_class = BlogCreateSerializer
            serializer = serializer_class(data=blog_data)
            if serializer.is_valid():
                try:
                    serializer.save()
                    response = {
                        "data": serializer.data,
                        "message": "Successfully created blog",
                        "status": status.HTTP_201_CREATED,
                    }
                except IntegrityError as e:
                    response = {
                        "data": [],
                        "message": f"An error occurred: {str(e)}",
                        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    }
            else:
                message = "blog creation failed!"
                if serializer.errors["thumbnail"]:
                    message = serializer.errors["thumbnail"][0]
                response = {
                    "data": serializer.errors,
                    "message": message,
                    "status": status.HTTP_400_BAD_REQUEST,
                }
        except Exception as e:
            response = {
                "data": [],
                "message": f"An error occurred: {str(e)}",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        return Response(response, status=response["status"])


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
        likesCount = Likes.objects.filter(post=post).count()
        commentCount = Comments.objects.filter(post=post, parent=None).count()
        # Create a copy of the serialized data and add the 'saved' and 'liked' fields
        post_data = serializer.data.copy()
        post_data["liked"] = liked
        post_data["saved"] = saved
        post_data["likesCount"] = likesCount
        post_data["commentCount"] = commentCount
        # Create the response dictionary
        response = {
            "data": post_data,
            "message": "Successfully retrieved A blog post",
            "status": status.HTTP_200_OK,
        }

    except Exception as e:
        response = {
            "data": None,
            "message": f"An error occurred: {str(e)}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

    return Response(response, status=response["status"])


@api_view(["GET"])
def getAllCommentsByPostId(request, pk):
    try:
        comments = Comments.objects.filter(post=pk, parent=None).order_by("-created_at")
        if not comments.exists():
            response = {
                "data": None,
                "message": "No comments found for this post.",
                "status": status.HTTP_404_NOT_FOUND,
            }
            return Response(response, status=response["status"])

        # Create an instance of the pagination class
        paginator = CustomLimitOffsetPagination()
        # Paginate the queryset
        paginated_posts = paginator.paginate_queryset(comments, request)

        # Serialize the paginated queryset
        serializer = CommentSerializer(paginated_posts, many=True)
        for comment in serializer.data:
            liked = (
                CommentLikes.objects.filter(
                    comment=comment["id"], author=request.user
                ).exists()
                if request.user.is_authenticated
                else False
            )
            commentCount = Comments.objects.filter(parent=comment["id"]).count()
            likesCount = CommentLikes.objects.filter(comment=comment["id"]).count()
            comment["liked"] = liked
            comment["likesCount"] = likesCount
            comment["commentCount"] = commentCount
            comment["created_at"] = format_date_time(comment["created_at"])
        # Create the response with pagination data
        paginated_response = paginator.get_paginated_response(serializer.data)
        data = paginated_response.data

        # Create the response dictionary
        response = {
            "data": data,
            "message": "Successfully retrieved the comments",
            "status": status.HTTP_200_OK,
        }
    except Exception as e:
        response = {
            "data": None,
            "message": f"An error occurred: {str(e)}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

    return Response(response, status=response["status"])


@api_view(["GET"])
def getAllReplyByCommentId(request, pk):
    try:
        if not request.user.is_authenticated:
            response = {
                "status": status.HTTP_403_FORBIDDEN,
                "message": "You are not allowed to access this resource.",
                "data": [],
            }
            return Response(response, status=response["status"])
        comments = Comments.objects.filter(parent=pk).order_by("-created_at")

        if not comments.exists():
            response = {
                "data": None,
                "message": "No reply found for this comment.",
                "status": status.HTTP_404_NOT_FOUND,
            }
            return Response(response, status=response["status"])

        # Create an instance of the pagination class
        paginator = CustomLimitOffsetPagination()
        # Paginate the queryset
        paginated_posts = paginator.paginate_queryset(comments, request)

        # Serialize the paginated queryset
        serializer = CommentSerializer(paginated_posts, many=True)
        for comment in serializer.data:
            liked = (
                CommentLikes.objects.filter(
                    comment=comment["id"], author=request.user
                ).exists()
                if request.user.is_authenticated
                else False
            )
            likesCount = CommentLikes.objects.filter(comment=comment["id"]).count()
            commentCount = Comments.objects.filter(parent=comment["id"]).count()
            comment["liked"] = liked
            comment["likesCount"] = likesCount
            comment["commentCount"] = commentCount
            comment["created_at"] = format_date_time(comment["created_at"])
        # Create the response with pagination data
        paginated_response = paginator.get_paginated_response(serializer.data)
        data = paginated_response.data
        response = {
            "data": data,
            "message": "Successfully retrieved the reply comments",
            "status": status.HTTP_200_OK,
        }
    except Exception as e:
        response = {
            "data": None,
            "message": f"An error occurred: {str(e)}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

    return Response(response, status=response["status"])


@api_view(["GET"])
def likeAPost(request, pk):
    try:
        if not request.user.is_authenticated:
            response = {
                "status": status.HTTP_403_FORBIDDEN,
                "message": "You are not allowed to access this resource.",
                "data": [],
            }
            return Response(response, status=response["status"])
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
        if not request.user.is_authenticated:
            response = {
                "status": status.HTTP_403_FORBIDDEN,
                "message": "You are not allowed to access this resource.",
                "data": [],
            }
            return Response(response, status=response["status"])
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


@api_view(["POST"])
def createComment(request, pk):
    try:
        if not request.user.is_authenticated:
            response = {
                "status": status.HTTP_403_FORBIDDEN,
                "message": "You are not allowed to access this resource.",
                "data": [],
            }
            return Response(response, status=response["status"])
        # Make a copy of request.data and add the author field
        comment_data = request.data.copy()
        if not comment_data.get("parent"):
            comment_data["parent"] = None
        if comment_data["parent"] is not None:
            parent = Comments.objects.filter(pk=comment_data["parent"])
            if not parent:
                response = {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": "Comment Not Found!.",
                    "data": [],
                }
                return Response(response, status=response["status"])

        post = Comments.objects.filter(pk=pk)
        if not post:
            response = {
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Post Not Found!.",
                "data": [],
            }
            return Response(response, status=response["status"])
        comment_data["author"] = request.user.id
        comment_data["post"] = pk
        serializer = CommentCreateSerializer(data=comment_data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "data": serializer.data,
                "message": "Successfully created Comment",
                "status": status.HTTP_201_CREATED,
            }
        else:
            response = {
                "data": serializer.errors,
                "message": "Comment creation failed!",
                "status": status.HTTP_400_BAD_REQUEST,
            }
    except Exception as e:
        response = {
            "data": [],
            "message": f"An error occurred: {str(e)}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    return Response(response, status=response["status"])


@api_view(["GET"])
def saveAPost(request, pk):
    try:
        if not request.user.is_authenticated:
            response = {
                "status": status.HTTP_403_FORBIDDEN,
                "message": "You are not allowed to access this resource.",
                "data": [],
            }
            return Response(response, status=response["status"])
        # Check if the post exists
        post = Posts.objects.get(pk=pk)

        # Check if the user has already liked the post
        save = Saved.objects.filter(author=request.user, post=post).first()

        if save:
            # User has already liked the post, so remove the like
            save.delete()
            message = "Blog removed from saved successfully"
        else:
            # User has not liked the post, so add a new like
            Saved.objects.create(author=request.user, post=post)
            message = "Blog saved successfully"

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
def getAllTags(request):
    try:
        tags = Tags.objects.all()

        # Create an instance of the pagination class
        paginator = CustomLimitOffsetPagination()
        # Paginate the queryset
        paginated_tags = paginator.paginate_queryset(tags, request)

        # Serialize the paginated queryset
        serializer = TagSerializer(paginated_tags, many=True)

        # Create the response with pagination data
        paginated_response = paginator.get_paginated_response(serializer.data)
        data = paginated_response.data
        response = {
            "data": data,
            "message": "Successfully retrieved all Tags",
            "status": status.HTTP_200_OK,
        }
        return Response(response, status=response["status"])

    except Exception as e:
        response = {
            "data": [],
            "message": f"An error occurred: {str(e)}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        return Response(response, status=response["status"])


@api_view(["GET"])
def getAUserProfile(request, username):
    try:
        if not request.user.is_authenticated:
            response = {
                "status": status.HTTP_403_FORBIDDEN,
                "message": "You are not allowed to access this resource.",
                "data": [],
            }
            return Response(response, status=response["status"])
        user = User.objects.get(username=username)
        serializer = UserSerializer(user)
        followingCount = Followings.objects.filter(follower=user).count()
        followerCount = Followings.objects.filter(following=user).count()
        postCount = Posts.objects.filter(author=user).count()
        user_data = serializer.data.copy()
        user_data["followingCount"] = followingCount
        user_data["followerCount"] = followerCount
        user_data["postCount"] = postCount
        # Create the response dictionary
        response = {
            "data": user_data,
            "message": "Successfully retrieved A user profile",
            "status": status.HTTP_200_OK,
        }
    except Exception as e:
        response = {
            "data": None,
            "message": f"An error occurred: {str(e)}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

    return Response(response, status=response["status"])


