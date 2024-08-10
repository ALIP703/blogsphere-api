from django.urls import path

from . import views

urlpatterns = [
    path("", views.getAllBlogs),
    path("tags", views.getAllTags),
    path("create-blog", views.CreateBlogView.as_view()),
    path("media/upload", views.FileUploadView.as_view(), name="file-upload"),
    path("blog/<int:pk>/", views.getABlog),
    path("blogs/profile/<int:pk>/", views.getAllBlogsByUserId),
    path("profile/<str:username>/", views.getAUserProfile),
    path("blog/<int:pk>/comments", views.getAllCommentsByPostId),
    path("comment/<int:pk>/reply", views.getAllReplyByCommentId),
    path("blog/<int:pk>/like", views.likeAPost),
    path("blog/<int:pk>/save", views.saveAPost),
    path("comment/<int:pk>/like", views.likeAComment),
    path("blog/<int:pk>/create-comment", views.createComment),
]
