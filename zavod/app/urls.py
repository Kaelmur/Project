from django.urls import path
from app import views

urlpatterns = [
    path("home/profile/", views.home, name="profile"),
    path("home/verify/", views.verify, name="verify"),
    path("home/verify_email", views.verify_email, name="verify_email")
]
