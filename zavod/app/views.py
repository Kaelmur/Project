from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.models import UserManage as CustomUser
from .models import Order, Pay
from .forms import PayForm
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle
import os


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


def pdf_create(order, content, order_id):
    pdf = SimpleDocTemplate(content, pagesize=A4)
    title = Paragraph(f"Check for order #{order_id} of {order.date_ordered.strftime('%d, %B, %Y')}")
    pdf.build([title])


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
        pdf_path = os.path.join(settings.BASE_DIR, "app", "receipts", "receipt.pdf")
        pdf_create(order, pdf_path, order.id)
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()
        email_send = EmailMessage(mail_subject, message, attachments=[("paycheck.pdf", pdf_content,
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
    ordering = ["-date_ordered"]
    context_object_name = "orders"
    paginate_by = 2


class OrderDetailView(DetailView):
    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PayForm()
        return context

    def post(self, request, *args, **kwargs):
        form = PayForm(self.request.POST, self.request.FILES, instance=self.get_object())
        if form.is_valid():
            file = Pay(file=request.FILES.get("file"), order=self.get_object())
            file.save()
            return redirect(request.path_info)


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
