from django.urls import path
from . import views, admin_views

app_name = "problems"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/", views.problem_detail, name="problem_detail"),
     path("admin/pending_submissions/", admin_views.pending_submissions, name="pending_submissions"),
    path("admin/submission/<int:pk>/", admin_views.submission_detail, name="submission_detail"),
]

