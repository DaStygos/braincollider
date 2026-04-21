from django.urls import path
from . import views

app_name = "staff"

urlpatterns = [
    path("pending_submissions/", views.pending_submissions, name="pending_submissions"),
    path("submission/<int:pk>/", views.submission_detail, name="submission_detail"),
    path("suggest_problem/", views.suggest_problem, name="suggest_problem"),
    #path("stats/", views.stats, name="stats"),
]
