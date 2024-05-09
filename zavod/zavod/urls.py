from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app import views as app_views
from users import views as user_views
from django.contrib.auth.decorators import login_required
from app.urls import guest_required


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("app.urls")),
    path("home/", user_views.register, name="register"),
    path("activate/<uidb64>/<token>", user_views.activate, name="activate"),
    path('login/', guest_required(user_views.login_user), name='login'),
    path('verify-email/<uidb64>/<token>/', user_views.verify_email, name='verify_email'),
    path("logout/", login_required(auth_views.LogoutView.as_view(template_name='users/logout.html')), name="logout"),
    path("activate-order/<int:pk>", app_views.activate_order, name="activate_order"),
    path('activate-security-order/<int:pk>', app_views.security_order_approved, name='security_approved'),
    path('moderator/login/', auth_views.LoginView.as_view(redirect_authenticated_user=True,
                                                          template_name='users/login.html'), name='admin_login'),
    path('user-role-change/<int:pk>', user_views.change_role, name='change-role')
]
