from django.contrib.auth.models import User
from django.db import models


class Tags(models.Model):
    value = models.CharField(max_length=250)
    label = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.label


class UploadedFile(models.Model):
    file = models.FileField(upload_to="uploads/%Y/%m/%d/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Posts(models.Model):
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=250, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    tags = models.ManyToManyField(Tags, related_name="posts")
    thumbnail = models.ImageField(upload_to="uploads/%Y/%m/%d/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Likes(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("author", "post")

    def __str__(self):
        return f"{self.author} likes {self.post}"


class Saved(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved")
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="saved")

    class Meta:
        unique_together = ("author", "post")

    def __str__(self):
        return f"{self.author} saved {self.post}"


class Followings(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        # Add a unique constraint on follower and following fields
        unique_together = ("follower", "following")

    def __str__(self):
        return f"{self.follower} followed {self.following}"


class Comments(models.Model):
    message = models.CharField(max_length=250)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message


class CommentLikes(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_likes"
    )
    comment = models.ForeignKey(
        Comments, on_delete=models.CASCADE, related_name="comment_likes"
    )

    def __str__(self):
        return f"{self.author} likes {self.comment}"


class Reports(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    post = models.ForeignKey(
        Posts,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reported_posts",
    )
    author = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reported_authors",
    )

    def __str__(self):
        return f"Report by {self.reporter}"


class Notifications(models.Model):
    title = models.CharField(max_length=250)
    messages = models.TimeField()

    def __str__(self):
        return f"Report by {self.title}"
