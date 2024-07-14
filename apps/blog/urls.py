from django.urls import path

from . import views

urlpatterns = [
    path("", views.getAllBlogs),
    path("create-blog", views.createBlog),
    path("blog/<int:pk>/", views.getABlog),
    path("blog/<int:pk>/comments", views.getAllCommentsByPostId),
    path("comments/<int:pk>/reply", views.getAllReplyByCommentId),
    path("blog/<int:pk>/like", views.likeAPost),
]
