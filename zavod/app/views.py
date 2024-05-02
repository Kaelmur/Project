from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from users.models import UserManage as CustomUser
from .models import Order
from django.contrib import messages


@login_required
def home(request):
    return render(request, "app/profile.html")


class AllOrdersListView(ListView, UserPassesTestMixin):
    model = Order
    template_name = 'app/orders.html'
    ordering = ["-date_ordered"]
    context_object_name = "all_orders"
    paginate_by = 2

    def test_func(self):
        return self.request.user.is_superuser


def verify(request):
    return render(request, "app/verify.html")


def verify_email(request):
    return render(request, "app/verify_email.html")


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ["registration_certificate", "mass"]
    success_url = "/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = "pending"
        mass = form.cleaned_data['mass']
        form.instance.price = mass * 20
        messages.success(self.request, 'Order created')
        return super().form_valid(form)


class OrderListView(ListView):
    model = Order
    template_name = 'app/profile.html'
    ordering = ["-date_ordered"]
    context_object_name = "orders"
    paginate_by = 2


class OrderDetailView(DetailView):
    model = Order


@login_required
def activate_order(request, pk):
    order = Order.objects.get(pk=pk)
    order.status = "continuing"
    order.save()
    messages.success(request, f"Order activated")
    return redirect("order-detail", order.id)


class UserListView(ListView, UserPassesTestMixin):
    model = CustomUser
    template_name = "app/users.html"
    context_object_name = "users"
    ordering = ["-id"]
    paginate_by = 2

    def test_func(self):
        return self.request.user.is_superuser
