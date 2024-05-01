from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Order
from django.contrib import messages


@login_required
def home(request):
    return render(request, "app/profile.html")


def verify(request):
    return render(request, "app/verify.html")


def verify_email(request):
    return render(request, "app/verify_email.html")


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ["registration_certificate", "mass"]
    success_url = "profile"

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Order created')
        return super().form_valid(form)
