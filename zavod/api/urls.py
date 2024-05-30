from django.urls import path
from .views import (OrderListView, OrderCreateView, LoginUserView, VerifyEmailView, RegisterUserView, ActivateEmail,
                    SecurityApproveOrderListView, SecurityOrderExitApprovedView, PaidOrderListView, OrderDetailView,
                    ActivateOrder)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='api-order-detail'),
    path('activate-order/<int:pk>/', ActivateOrder.as_view(), name='api-activate_order'),
    path('login/', LoginUserView.as_view(), name='api-login'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='api-verify-email'),
    path('register/', RegisterUserView.as_view(), name='api-register'),
    path('activate/<uidb64>/<token>/', ActivateEmail.as_view(), name='api-activate'),
    path('security_approve_orders/', SecurityApproveOrderListView.as_view(), name='api-security-approve-orders'),
    path('security_order_exit_approve/<int:pk>', SecurityOrderExitApprovedView.as_view(), name='api-security-exit'),
    path('paid_orders/', PaidOrderListView.as_view(), name='paid-orders')
]
