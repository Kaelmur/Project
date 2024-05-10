from django.urls import path
from app import views
from .views import (OrderCreateView, OrderListView, OrderDetailView, UserListView, AllOrdersListView, PaidOrderListView,
                    UserDetailView, SecurityOrderListView, LoaderOrderListView, SecurityApproveOrderListView)
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import user_passes_test


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
    path("orders/", AllOrdersListView.as_view(), name="orders"),
    path('paid_orders/', PaidOrderListView.as_view(), name='paid-orders'),
    path('security_orders/', SecurityOrderListView.as_view(), name='security_orders'),
    path('security_approve_orders/', SecurityApproveOrderListView.as_view(), name='security_approve_orders'),
    path('security_order_exit_approve/<int:pk>', views.security_order_exit_approved, name='security-exit'),
    path('loader_orders/', LoaderOrderListView.as_view(), name='loader_orders'),
    path("verify/", guest_required(views.verify), name="verify"),
    path("verify_email/", guest_required(views.verify_email), name="verify_email"),
    path("order", OrderCreateView.as_view(), name="order"),
    path("order/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path('order_measurements/<int:pk>', views.measurements, name='order-measurements'),
    path('order_approve_measurements/<int:pk>', views.measurements_approved, name='order-approve-mesurements'),
    path("users/", UserListView.as_view(), name='users'),
    path("users/<int:pk>/", UserDetailView.as_view(), name='user-detail'),
    path('download/<int:file_id>/', views.download_check, name='download-check')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
