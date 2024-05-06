from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from users.models import UserManage as CustomUser
from django.contrib.auth.models import Group
from .models import Order, Pay
from .forms import PayForm
from django.http import FileResponse
from django.contrib import messages
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle
import io
import os


def user_belongs_to_security_group(user):
    security_group = Group.objects.get(name='security')
    return security_group in user.groups.all()


@login_required
def home(request):
    return render(request, "app/profile.html")


class PaidOrderListView(UserPassesTestMixin, ListView):
    model = Order
    template_name = 'app/payed_orders.html'
    context_object_name = 'paid_orders'
    paginate_by = 2

    def test_func(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        return self.request.user.is_superuser or user_belongs_to_security_group(user)

    def get_queryset(self):
        return Order.objects.filter(status='модерация').order_by("-date_ordered")


class AllOrdersListView(UserPassesTestMixin, ListView):
    model = Order
    template_name = 'app/orders.html'
    ordering = ["-date_ordered"]
    context_object_name = "all_orders"
    paginate_by = 2

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return Order.objects.exclude(status='неоплачено')


def verify(request):
    return render(request, "app/verify.html")


@user_passes_test(lambda u: u.is_superuser)
def download_check(request, file_id):
    file = get_object_or_404(Pay, pk=file_id)
    file_url = file.file.url[1:]
    file_extension = os.path.splitext(file_url)[1].lower()
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    if file_extension in allowed_extensions:
        content_type = 'application/pdf' if file_extension == '.pdf' else 'image/*'
        response = FileResponse(open(file_url, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file.id}{file_extension}"'
        return response


def verify_email(request):
    return render(request, "app/verify_email.html")


def pdf_create(order, order_id):
    buf = io.BytesIO()
    pdf = SimpleDocTemplate(buf, pagesize=A4)
    title = Paragraph(f"Check for order #{order_id} of {order.date_ordered.strftime('%d, %B, %Y')}")
    pdf.build([title])
    buf.seek(0)
    return buf.getvalue()


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ["registration_certificate", "fraction", "mass"]
    success_url = "/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        mass = form.cleaned_data['mass']
        form.instance.price = mass * 20
        response = super().form_valid(form)
        order = form.instance
        mail_subject = f"Оплата заказа #{order.id}"
        message = "Check pdf file below to checkout"
        pdf = pdf_create(order, order.id)
        email_send = EmailMessage(mail_subject, message, attachments=[("paycheck.pdf", pdf,
                                                                       'application/pdf')], to=[self.request.user.email])
        if email_send.send():
            messages.success(self.request, 'Order created, paycheck send to your email!')
        else:
            messages.error(self.request, f"Problem sending email to {self.request.user.email},"
                                          f""f"please check if you typed it correctly")
        return response


class OrderListView(ListView):
    model = Order
    template_name = 'app/profile.html'
    context_object_name = "orders"
    paginate_by = 2

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-date_ordered")


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = CustomUser
    template_name = 'users/user_detail.html'

    def test_func(self):
        return self.request.user.is_superuser


class OrderDetailView(UserPassesTestMixin, DetailView):
    model = Order

    def test_func(self):
        order = self.get_object()
        return self.request.user == order.user or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PayForm()
        return context

    def post(self, request, *args, **kwargs):
        form = PayForm(self.request.POST, self.request.FILES, instance=self.get_object())
        if form.is_valid():
            file = Pay(file=request.FILES.get("file"), order=self.get_object())
            file.save()
            order = self.get_object()
            order.status = 'модерация'
            order.save()
            messages.success(self.request, 'Чек принят. Ждите подтверждения')
            return redirect(request.path_info)


@user_passes_test(lambda u: u.is_superuser)
def activate_order(request, pk):
    order = Order.objects.get(pk=pk)
    order.status = "оплачен"
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
