from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("sign-out", views.signOut, name="sign-out"),
    path("sign-in", views.signIn, name="sign-in"),
    path("sign-up", views.signUp, name="sign-up"),
    path("auth", views.isAuthenticated, name="user_auth"),
    path("token", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
]
