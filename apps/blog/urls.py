from django.urls import path

from . import views

urlpatterns = [
    path("", views.blogs),
    path("create-blog", views.createBlog),
]
