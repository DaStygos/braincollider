from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("mentions-legales/", views.legal_notice, name="legal_notice"),
    path("confidentialite/", views.privacy, name="privacy"),
    path("cgu/", views.terms, name="terms"),
]
