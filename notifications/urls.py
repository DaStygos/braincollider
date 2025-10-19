from . import views
from django.urls import path

app_name = "notifications"

urlpatterns = [
    path('', views.notifications_list, name='notifications_list'),
    path('mark-as-read/<int:pk>/', views.mark_as_read, name='mark_as_read'),
]
