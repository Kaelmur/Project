from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from .models import UserManage as CustomUser

# def login_user(request):
#     if request.method == "POST":
#         form = UserLoginForm(request.POST)
#         if form.is_valid():
#             n


@user_passes_test(lambda u: not u.is_authenticated, login_url="zavod-home")
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['username']
            user = CustomUser.objects.create_user(email=email, username=name)
            user.is_active = False
            activate_email(request, user, form.cleaned_data.get("email"))
            return redirect("verify")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


def activate_email(request, user, to_email):
    token = default_token_generator.make_token(user)
    mail_subject = "Verify your email"
    message = render_to_string("users/template_change_email.html", {
        "user": user,
        "domain": get_current_site(request).domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": token,
        "protocol": "https" if request.is_secure() else "http",
    })
    email_send = EmailMessage(mail_subject, message, to=[to_email])
    if email_send.send():
        messages.success(request, f"Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
        received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.")
    else:
        messages.error(request, f"Problem sending email to {to_email}, please check if you typed it correctly")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, f"Your account {user.username} has been created!")
        return redirect('profile')
