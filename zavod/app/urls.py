from django.urls import path
from app import views
from .views import OrderCreateView

urlpatterns = [
    path("profile/", views.home, name="profile"),
    path("verify/", views.verify, name="verify"),
    path("verify_email", views.verify_email, name="verify_email"),
    path("order", OrderCreateView.as_view(), name="order")
]
