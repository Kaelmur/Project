from django.urls import path
from app import views
from .views import OrderCreateView, OrderListView, OrderDetailView, UserListView, AllOrdersListView, PaidOrderListView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", login_required(OrderListView.as_view()), name="profile"),
    path("orders/", AllOrdersListView.as_view(), name="orders"),
    path('paid_orders/', PaidOrderListView.as_view(), name='paid-orders'),
    path("verify/", views.verify, name="verify"),
    path("verify_email", views.verify_email, name="verify_email"),
    path("order", OrderCreateView.as_view(), name="order"),
    path("order/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("users/", login_required(UserListView.as_view()), name='users')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
