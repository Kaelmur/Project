from django.urls import path
from .views import (OrderListView, OrderCreateView, LoginUserView, VerifyEmailView, RegisterUserView, ActivateEmail,
                    SecurityApproveOrderListView, SecurityOrderExitApprovedView, PaidOrderListView, OrderDetailView,
                    ActivateOrder, Measurement, MeasureApproved, LoaderApprove, SecurityOrderApprove, FractionPrices,
                    FractionPriceCreateUpdate, UserList, UserDetail, ChangeRole, DownloadCheck)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .yasg import urlpatterns as doc_urls
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('orders/', OrderListView.as_view(), name='api-order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='api-order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='api-order-detail'),
    path('activate-order/<int:pk>/', ActivateOrder.as_view(), name='api-activate_order'),
    path('login/', LoginUserView.as_view(), name='api-login'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='api-verify-email'),
    path('register/', RegisterUserView.as_view(), name='api-register'),
    path('activate/<str:uidb64>/<str:token>/', ActivateEmail.as_view(), name='api-activate'),
    path('order_measurements/<int:pk>', Measurement.as_view(), name='api-order-measurements'),
    path('order_approve_measurements/<int:pk>', MeasureApproved.as_view(), name='api-order-approve-measurements'),
    path('activate-loader-order/<int:pk>', LoaderApprove.as_view(), name='api-loader_approved'),
    path('security_approve_orders/', SecurityApproveOrderListView.as_view(), name='api-security-approve-orders'),
    path('activate-security-order/<int:pk>', SecurityOrderApprove.as_view(), name='api-security_approved'),
    path('security_order_exit_approve/<int:pk>', SecurityOrderExitApprovedView.as_view(), name='api-security-exit'),
    path('paid_orders/', PaidOrderListView.as_view(), name='api-paid-orders'),
    path('fraction_prices/', FractionPrices.as_view(), name='api-fraction-price'),
    path('fraction_price_add/', FractionPriceCreateUpdate.as_view(), name='api-fraction-price'),
    path("users/", UserList.as_view(), name='api-users'),
    path('users/<int:pk>/', UserDetail.as_view(), name='api-user-detail'),
    path('user-role-change/<int:pk>', ChangeRole.as_view(), name='api-change-role'),
    path('download/<int:file_id>/', DownloadCheck.as_view(), name='api-download-check'),
]

urlpatterns += doc_urls
