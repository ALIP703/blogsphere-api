from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.
def blogs(request):
    try:
        # posts = Posts.objects.all()

        # current_time = timezone.now()
        # today = current_time.date()
        # yesterday = today - timedelta(days=1)

        # posts_list = []

        # for post in posts:
        #     created_at_date = post.created_at.date()
        #     if created_at_date == today:
        #         created_at_display = "Today"
        #     elif created_at_date == yesterday:
        #         created_at_display = "Yesterday"
        #     else:
        #         created_at_display = post.created_at

        #     liked_by_current_user = False
        #     if request.user.is_authenticated:
        #         try:
        #             Likes.objects.get(post=post, author=request.user)
        #             liked_by_current_user = True
        #         except Likes.DoesNotExist:
        #             liked_by_current_user = False

        #     post_dict = {
        #         "id": post.id,
        #         "title": post.title,
        #         "content": post.content,
        #         "created_at": created_at_display,
        #         "is_liked": liked_by_current_user,
        #         # Add other fields as needed
        #     }
        #     posts_list.append(post_dict)

        response = {
            "data": "posts_list",
            "message": "successfully retrieved all blogs",
            "status": 200,
        }

    except Exception as e:
        response = {
            "data": [],
            "message": f"An error occurred: {str(e)}",
            "status": 500,
        }

    # Return the JSON response with posts and their associated data
    return JsonResponse(response, safe=False)
