"""
URL configuration for zavod project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app import views as app_views
from users import views as user_views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("app.urls")),
    path("home/", user_views.register, name="register"),
    path("activate/<uidb64>/<token>", user_views.activate, name="activate"),
    path('login/', user_views.login_user, name='login'),
    path('verify-email/<uidb64>/<token>/', user_views.verify_email, name='verify_email'),
    path("logout/", login_required(auth_views.LogoutView.as_view(template_name='users/logout.html')), name="logout"),
    path("activate-order/<int:pk>", app_views.activate_order, name="activate_order")
]
