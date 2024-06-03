from .views import (OrderCreateView, OrderListView, OrderDetailView, UserListView, PaidOrderListView,
                    UserDetailView, SecurityApproveOrderListView, security_order_exit_approved, measurements_approved,
                    measurements, download_check, fraction_price, activate_order, security_order_approved,
                    loader_order_approved)
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path


def guest_required(view_func):
    """
    Decorator for views that checks that the user is a guest (i.e., not logged in).
    """
    decorator = user_passes_test(
        lambda u: not u.is_authenticated,
        login_url='/'
    )
    return decorator(view_func)


urlpatterns = [
    path("", login_required(OrderListView.as_view()), name="profile"),
    path("order", OrderCreateView.as_view(), name="order"),
    path("order/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path('paid_orders/', PaidOrderListView.as_view(), name='paid-orders'),
    path('security_approve_orders/', SecurityApproveOrderListView.as_view(), name='security_approve_orders'),
    path('activate-security-order/<int:pk>', security_order_approved, name='security_approved'),
    path("activate-order/<int:pk>", activate_order, name="activate_order"),
    path('activate-loader-order/<int:pk>', loader_order_approved, name='loader_approved'),
    path('security_order_exit_approve/<int:pk>', security_order_exit_approved, name='security-exit'),
    path('order_measurements/<int:pk>', measurements, name='order-measurements'),
    path('order_approve_measurements/<int:pk>', measurements_approved, name='order-approve-measurements'),
    path("users/", UserListView.as_view(), name='users'),
    path("users/<int:pk>/", UserDetailView.as_view(), name='user-detail'),
    path('download/<int:file_id>/', download_check, name='download-check'),
    path('fraction_price/', fraction_price, name='fraction-price'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
