from django.urls import path
from . import views

app_name = "problems"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/save/", views.toggle_saved_problem, name="toggle_saved_problem"),
    path("<int:pk>/", views.problem_detail, name="problem_detail"),
]
