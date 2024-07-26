from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["username"] = user.username
        token["email"] = user.email
        token["userId"] = user.id
        if hasattr(user, "profile"):
            token["image"] = user.profile.image.url  # Assuming `image` is an ImageField
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add additional data to the response
        data["username"] = self.user.username
        data["email"] = self.user.email
        data["userId"] = self.user.id
        if hasattr(self.user, "profile"):
            data["image"] = (
                self.user.profile.image.url
            )  # Assuming `image` is an ImageField
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(["GET"])
def signOut(request):
    logout(request)
    response = {
        "status": status.HTTP_200_OK,
        "message": "Logout Successfully",
        "data": [],
    }
    return Response(response)


@api_view(["POST"])
def signIn(request):
    username = request.data.get("username")
    password = request.data.get("password")
    response = {}

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        session_id = request.session.session_key
        response = {
            "status": status.HTTP_200_OK,
            "message": "Login Successfully",
            "data": {
                "username": user.username,
                "session_id": session_id,
            },
        }
    else:
        response = {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Username or password incorrect",
            "data": [],
        }

    return Response(response)


@api_view(["POST"])
def signUp(request):
    try:
        user_data = request.data.copy()
        if user_data["password"] != user_data["confirmPassword"]:
            response = {
                "data": None,
                "message": "Confirm Password is not same!",
                "status": status.HTTP_400_BAD_REQUEST,
            }
            return Response(response, status=response["status"])
        # Hash the password before saving
        user_data["password"] = make_password(user_data.get("password"))
        serializer = UserSerializer(data=user_data)
        if serializer.is_valid():
            try:
                serializer.save()
                response = {
                    "data": serializer.data,
                    "message": "Successfully created User",
                    "status": status.HTTP_201_CREATED,
                }
            except IntegrityError as e:
                response = {
                    "data": [],
                    "message": f"An error occurred: {str(e)}",
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
        else:
            # Check for unique constraint errors
            errors = serializer.errors
            if "username" in errors:
                response = {
                    "data": None,
                    "message": "A user with that username already exists!",
                    "status": status.HTTP_400_BAD_REQUEST,
                }
                return Response(response, status=response["status"])
            print(errors)
            response = {
                "data": errors,
                "message": "User creation failed!",
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
def isAuthenticated(request):
    if not request.user.is_authenticated:
        return Response(
            {
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "You are not authenticated.",
                "data": [],
            }
        )
    else:
        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "You are authenticated.",
                "data": [],
            }
        )
