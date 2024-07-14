from django.contrib import admin

from .models import (
    CommentLikes,
    Comments,
    Followings,
    Likes,
    Posts,
    Reports,
    Saved,
    Tags,
)

# Register your models here.

admin.site.register(Comments)
admin.site.register(CommentLikes)
admin.site.register(Followings)
admin.site.register(Likes)
admin.site.register(Posts)
admin.site.register(Reports)
admin.site.register(Tags)
admin.site.register(Saved)
