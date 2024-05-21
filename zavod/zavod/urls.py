from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app import views as app_views
from users import views as user_views
from django.contrib.auth.decorators import login_required
from app.urls import guest_required
from users.forms import CustomAuthenticationForm


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("app.urls")),
    path("register/", user_views.register, name="register"),
    path("activate/<uidb64>/<token>", user_views.activate, name="activate"),
    path('login/', guest_required(user_views.login_user), name='login'),
    path('verify-email/<uidb64>/<token>/', user_views.verify_email, name='verify_email'),
    path("logout/", login_required(auth_views.LogoutView.as_view()), name="logout"),
    path("activate-order/<int:pk>", app_views.activate_order, name="activate_order"),
    path('activate-security-order/<int:pk>', app_views.security_order_approved, name='security_approved'),
    path('activate-loader-order/<int:pk>', app_views.loader_order_approved, name='loader_approved'),
    path('moderator/login/', auth_views.LoginView.as_view(redirect_authenticated_user=True,
                                                          authentication_form=CustomAuthenticationForm,
                                                          template_name='pages/admin_login.html'), name='admin_login'),
    path('user-role-change/<int:pk>', user_views.change_role, name='change-role')
]
