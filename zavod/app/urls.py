from django.urls import path
from app import views

urlpatterns = [
    path("home/profile/", views.home, name="profile"),
    path("home/verify/", views.verify, name="verify")
]
