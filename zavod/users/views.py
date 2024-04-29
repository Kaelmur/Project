from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserRegisterForm
from django.contrib import messages


@user_passes_test(lambda u: not u.is_authenticated, login_url="zavod-home")
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Your account {username} has been created!")
            authenticate(username=form.cleaned_data['username'])
            login(request, new_user)
            return redirect("profile")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})
