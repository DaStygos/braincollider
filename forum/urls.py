from django.urls import path

from . import views

app_name = "forum"

urlpatterns = [
    path("", views.topic_list, name="topic_list"),
    path("topics/new/", views.topic_create, name="topic_create"),
    path("topics/<int:topic_id>/", views.topic_detail, name="topic_detail"),
    path("topics/<int:topic_id>/reply/", views.post_create, name="post_create"),
]
