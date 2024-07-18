from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="user/profile/")
    bio = models.CharField(max_length=300)

    def __str__(self):
        return self.user.username
