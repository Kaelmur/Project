from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from users.models import UserManage as CustomUser
from django.contrib.auth.models import Group
from .models import Order, Pay, FractionPrice
from .forms import PayForm, MeasureForm, MeasureApprovedForm, FractionPriceForm
from django.http import FileResponse
from django.contrib import messages
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.db.models import Q
import io
import os
import math


def user_belongs_to_security_group(user):
    security_group = Group.objects.get(name='security')
    return security_group in user.groups.all()


def user_belongs_to_loader_group(user):
    loader_group = Group.objects.get(name='loader')
    return loader_group in user.groups.all()


class LoaderOrderListView(UserPassesTestMixin, ListView):
    model = Order
    template_name = 'app/loader_orders.html'
    context_object_name = 'loader_orders'
    paginate_by = 2

    def test_func(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        return user_belongs_to_loader_group(user)

    def get_queryset(self):
        return Order.objects.filter(step='загрузка').order_by("-date_ordered")


class SecurityOrderListView(UserPassesTestMixin, ListView):
    model = Order
    template_name = 'app/security_orders.html'
    context_object_name = 'security_orders'
    paginate_by = 2

    def test_func(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        return user_belongs_to_security_group(user)

    def get_queryset(self):
        return Order.objects.filter(Q(status='оплачен') | Q(status='выехал')).order_by("-date_ordered")


class SecurityApproveOrderListView(UserPassesTestMixin, ListView):
    model = Order
    template_name = 'app/security_approve_orders.html'
    context_object_name = 'security_approve_orders'
    paginate_by = 2

    def test_func(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        return user_belongs_to_security_group(user)

    def get_queryset(self):
        return Order.objects.filter(step='охрана-выход').order_by("-date_ordered")


class PaidOrderListView(UserPassesTestMixin, ListView):
    model = Order
    template_name = 'paid_orders.html'
    context_object_name = 'paid_orders'
    paginate_by = 1

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return Order.objects.filter(status='модерация').order_by("-date_ordered")


class AllOrdersListView(UserPassesTestMixin, ListView):
    model = Order
    template_name = 'app/orders.html'
    context_object_name = "all_orders"
    paginate_by = 2

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return Order.objects.exclude(status='неоплачено').order_by("-date_ordered")


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


def pdf_create(order, fraction, price, price_without_nds, price_nds):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    pdfmetrics.registerFont(TTFont('calibri', 'calibri.ttf'))
    can.setFont("calibri", 12)
    can.drawString(185, 812, f"Счет на предоплату № {order.id} от {order.date_ordered.strftime("%d.%m.%Y")} г.")
    can.setFont("calibri", 10)
    can.drawString(110, 450, f'{order.user.username}{order.user.iin}, {order.user.address_index}, Республика Казахстан, г.Актобе')
    can.drawString(90, 412, f'{order.user.username} {order.user.iin}')
    can.drawString(115, 385, f'{order.user.address_index}, Республика Казахстан, Актюбинская обл., г.Актобе')
    can.drawString(175, 181, str(order.mass))
    can.drawString(202, 181, str(fraction.price))
    can.drawString(252, 181, str(price_without_nds))
    can.drawString(252, 143, str(price_without_nds))
    can.drawString(345, 143, str(price_nds))
    can.drawString(345, 181, str(price_nds))
    can.drawString(510, 181, str(price))
    can.drawString(510, 143, str(price))
    can.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(open("./check.pdf", "rb"))
    output = PdfWriter()
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)
    output_pdf_bytes_final = io.BytesIO()
    output.write(output_pdf_bytes_final)
    output_pdf_bytes_final.seek(0)
    return output_pdf_bytes_final.getvalue()


class OrderCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Order
    fields = ["registration_certificate", "fraction", "mass", 'buyer']
    success_url = "/"

    def test_func(self):
        return not self.request.user.groups.exists()

    def form_valid(self, form):
        form.instance.user = self.request.user
        mass = form.cleaned_data['mass']
        buyer = form.cleaned_data['buyer']
        fraction = form.cleaned_data['fraction']
        fractions_price = FractionPrice.objects.get(fraction=fraction)
        price_without_nds = mass * float(fractions_price.price)
        price_nds = (mass * float(fractions_price.price)) * 0.12
        form.instance.price = price_without_nds + (price_without_nds * 0.12)
        response = super().form_valid(form)
        order = form.instance
        if buyer == "юр.лицо":
            mail_subject = f"Оплата заказа #{order.id}"
            message = "Check pdf file below to checkout"
            pdf = pdf_create(order, fractions_price, form.instance.price, price_without_nds, price_nds)
            email_send = EmailMessage(mail_subject, message, attachments=[("paycheck.pdf", pdf,
                                                                           'application/pdf')],
                                      to=[self.request.user.email])
            if email_send.send():
                messages.success(self.request, 'Order created, paycheck send to your email!')
            else:
                messages.error(self.request, f"Problem sending email to {self.request.user.email},"
                                              f""f"please check if you typed it correctly")
                return redirect("order-detail", order.id)
        else:
            order.status = "оплачен"
            order.save()
            messages.success(self.request, f"Order activated")
            return redirect("order-detail", order.id)
        return response


class OrderListView(ListView):
    model = Order
    template_name = 'index.html'
    context_object_name = "orders"
    paginate_by = 2

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.exclude(status='неоплачено').order_by("-date_ordered")
        else:
            return Order.objects.filter(user=self.request.user).order_by("-date_ordered")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_orders'] = Order.objects.exclude(status='неоплачено').count()
        return context


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


@user_passes_test(lambda u: u.groups.filter(name='security').exists())
def security_order_approved(request, pk):
    order = Order.objects.get(pk=pk)
    order.status = 'выполняется'
    order.step = 'весы'
    order.save()
    messages.success(request, f"Заказ подтвержден")
    return redirect('security_orders')


@user_passes_test(lambda u: u.groups.filter(name='loader').exists())
def loader_order_approved(request, pk):
    order = Order.objects.get(pk=pk)
    order.step = 'весы-подтверждение'
    order.save()
    messages.success(request, f"Загрузка подтверждена")
    return redirect('loader_orders')


class UserListView(UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = "users.html"
    context_object_name = "users"
    ordering = ["-id"]
    paginate_by = 2

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(is_superuser=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = CustomUser.objects.exclude(is_superuser=True).count()
        return context


@user_passes_test(lambda u: u.is_superuser)
def measurements(request, pk):
    if request.method == "POST":
        form = MeasureForm(request.POST)
        if form.is_valid():
            lifting_capacity = form.cleaned_data['mass']
            manufactory = form.cleaned_data['manufactory']
            order = Order.objects.get(pk=pk)
            order.manufactory = manufactory
            if int(order.cycle) == 0:
                order.cycle = math.ceil(int(order.mass) / int(lifting_capacity))
                order.weight_left = order.mass
            order.step = 'загрузка'
            order.save()
            messages.success(request, f"Заказ взвешен и подтвержден!")
            return redirect("order-detail", order.id)
    else:
        form = MeasureForm()
    return render(request, 'app/order_measurements.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def measurements_approved(request, pk):
    if request.method == 'POST':
        form = MeasureApprovedForm(request.POST)
        if form.is_valid():
            measured_weight = form.cleaned_data['mass']
            order = Order.objects.get(pk=pk)
            order.weight_left = float(order.weight_left) - float(measured_weight)
            order.step = 'охрана-выход'
            order.save()
            messages.success(request, f"Заказ взвешен и подтвержден!")
            return redirect('orders')
    else:
        form = MeasureApprovedForm()
    return render(request, 'app/order_approved_measurements.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def fraction_price(request):
    if request.method == "POST":
        form = FractionPriceForm(request.POST)
        if form.is_valid():
            fraction_price_instance = form.save(commit=False)
            fraction = form.cleaned_data['fraction']
            existing_fraction_price = FractionPrice.objects.filter(fraction=fraction).first()
            if existing_fraction_price:
                existing_fraction_price.price = fraction_price_instance.price
                existing_fraction_price.save()
                messages.success(request, f"Цена на фракцию обновлена")
            else:
                fraction_price_instance.save()
                messages.success(request, f"Цена на фракцию установлена")
            return redirect('profile')
    else:
        form = FractionPriceForm()
    return render(request, "app/fraction_price.html", {"form": form})


@user_passes_test(lambda u: u.groups.filter(name='security').exists())
def security_order_exit_approved(request, pk):
    order = Order.objects.get(pk=pk)
    order.status = 'выехал'
    order.step = 'охрана'
    order.cycle = int(order.cycle) - 1
    if int(order.cycle) <= 0:
        order.step = 'закончен'
        order.status = 'закончен'
    order.save()
    messages.success(request, f"Выезд зазачика подтвержден")
    return redirect('security_approve_orders')
