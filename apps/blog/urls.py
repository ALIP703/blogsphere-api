from django.urls import path

from . import views

urlpatterns = [
    path("", views.getAllBlogs),
    path("create-blog", views.createBlog),
    path("blog/<int:pk>/", views.getABlog),
]
