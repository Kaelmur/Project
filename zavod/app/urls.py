from django.urls import path
from app import views
from .views import OrderCreateView, OrderListView, OrderDetailView, UserListView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("", login_required(OrderListView.as_view()), name="profile"),
    path("verify/", views.verify, name="verify"),
    path("verify_email", views.verify_email, name="verify_email"),
    path("order", OrderCreateView.as_view(), name="order"),
    path("order/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("users/", login_required(UserListView.as_view()), name='users')
]
