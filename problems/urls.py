from django.urls import path
from . import views

app_name = "problems"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/", views.problem_detail, name="problem_detail"),
]

