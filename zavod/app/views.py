from .forms import PayForm, MeasureForm, MeasureApprovedForm, FractionPriceForm, OrderForm, SearchForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from users.models import UserManage as CustomUser
from .models import Order, Pay, FractionPrice
from reportlab.pdfbase.ttfonts import TTFont
from django.contrib.auth.models import Group
from django.core.mail import EmailMessage
from reportlab.pdfbase import pdfmetrics
from PyPDF2 import PdfWriter, PdfReader
from reportlab.lib.pagesizes import A4
from django.http import FileResponse
from django.contrib import messages
from reportlab.pdfgen import canvas
from django.utils import timezone
from .tasks import send_pay_task
from django.db.models import Q
import json
import math
import os
import io


# Validators
def user_belongs_to_security_group(user):
    security_group = Group.objects.get(name='security')
    return security_group in user.groups.all()


def user_belongs_to_loader_group(user):
    loader_group = Group.objects.get(name='loader')
    return loader_group in user.groups.all()


# Order Class Views
class OrderCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'new-order.html'
    success_url = "/"

    def test_func(self):
        return not self.request.user.groups.exists()

    def form_valid(self, form):
        form.instance.user = self.request.user
        mass = form.cleaned_data['mass']
        buyer = form.cleaned_data['buyer']
        fraction = form.cleaned_data['fraction']
        date_reserved = form.cleaned_data['date_reserved']
        local_time = timezone.localtime(date_reserved)
        form.instance.date_reserved = local_time
        fractions_price = FractionPrice.objects.get(fraction=fraction)
        price_without_nds = mass * float(fractions_price.price)
        price_nds = (mass * float(fractions_price.price)) * 0.12
        form.instance.price = price_without_nds + (price_without_nds * 0.12)
        response = super().form_valid(form)
        order = form.instance
        if buyer == "юр.лицо":
            mail_subject = f"Оплата заказа #{order.id}"
            message = "PDF файл с предоплатой"
            pdf = pdf_create(order, fractions_price, form.instance.price, price_without_nds, price_nds)
            send_pay(self.request, self.request.user, pdf, mail_subject, message, order)
        else:
            order.status = "оплачен"
            order.save()
            messages.success(self.request, f"Order activated")
            return redirect("order-detail", order.id)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Order.objects.all()
        reserved_slots = [
            order.date_reserved.strftime('%Y-%m-%d %H:%M:%S')
            for order in orders
        ]
        context['reserved_slots'] = reserved_slots
        return context


class OrderListView(ListView):
    model = Order
    template_name = 'index.html'
    context_object_name = "orders"
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        search_query = self.request.GET.get('query')

        if user.is_superuser:
            queryset = Order.objects.exclude(status='неоплачено').order_by("-date_ordered")
            if search_query:
                queryset = queryset.filter(id__icontains=search_query)
            return queryset
        elif user_belongs_to_security_group(user):
            return Order.objects.filter(Q(status='оплачен') | Q(status='выехал')).order_by("-date_ordered")
        elif user_belongs_to_loader_group(user):
            return Order.objects.filter(step='загрузка').order_by("-date_ordered")
        else:
            return Order.objects.filter(user=self.request.user).order_by("-date_ordered")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_orders = Order.objects.exclude(status='неоплачено').order_by("-date_ordered")
        bought_orders = Order.objects.exclude(status='неоплачено')
        bought_data = [
            {key: value.strftime("%Y-%m-%d %H:%M:%S") for key, value in order.items() if key == 'date_ordered'}
            for order in bought_orders.values()
        ]
        orders_data = [
            {key: value for key, value in order.items() if key == 'fraction'}
            for order in all_orders.values()
        ]
        context['bought_data'] = json.dumps(bought_data)
        context['orders_data'] = json.dumps(orders_data)
        context['total_orders'] = Order.objects.exclude(status='неоплачено').count()
        context['user_total_orders'] = Order.objects.filter(user=self.request.user).count()
        context['search_form'] = SearchForm(self.request.GET)
        context['local'] = timezone.now()
        return context


class OrderDetailView(UserPassesTestMixin, DetailView):
    model = Order
    template_name = 'order-detail.html'

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
        else:
            messages.error(self.request, "Неверный формат файла.")
            return redirect(request.path_info)


class SecurityApproveOrderListView(UserPassesTestMixin, ListView):
    model = Order
    template_name = 'pages/security_approve_orders.html'
    context_object_name = 'security_approve_orders'
    paginate_by = 5

    def test_func(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        return user_belongs_to_security_group(user)

    def get_queryset(self):
        return Order.objects.filter(step='охрана-выход').order_by("-date_ordered")


class PaidOrderListView(UserPassesTestMixin, ListView):
    model = Order
    template_name = 'paid_orders.html'
    context_object_name = 'paid_orders'
    paginate_by = 5

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        search_query = self.request.GET.get('query')
        queryset = Order.objects.filter(status='модерация').order_by("-date_ordered")
        if search_query:
            queryset = Order.objects.filter(Q(status='модерация') & Q(id__icontains=search_query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(self.request.GET)
        return context


# User Class Views
class UserListView(UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = "users.html"
    context_object_name = "users"
    ordering = ["-id"]
    paginate_by = 5

    def test_func(self):
        return self.request.user.is_superuser or user_belongs_to_security_group(self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('query')

        if self.request.user.is_superuser:
            if search_query:
                queryset = CustomUser.objects.filter(Q(username__icontains=search_query) | Q(id__icontains=search_query))
            return queryset.exclude(is_superuser=True)
        return queryset.exclude(is_superuser=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = CustomUser.objects.exclude(is_superuser=True).count()
        context['search_form'] = SearchForm(self.request.GET)
        return context


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = CustomUser
    template_name = 'pages/user_detail.html'

    def test_func(self):
        return self.request.user.is_superuser or user_belongs_to_security_group(self.request.user)


# Function based views
@user_passes_test(lambda u: u.is_superuser)
def activate_order(request, pk):
    order = Order.objects.get(pk=pk)
    order.status = "оплачен"
    order.save()
    messages.success(request, f"Заказ активирован")
    return redirect("order-detail", order.id)


@user_passes_test(lambda u: u.groups.filter(name='security').exists())
def security_order_approved(request, pk):
    order = Order.objects.get(pk=pk)
    order.status = 'выполняется'
    order.step = 'весы'
    order.save()
    messages.success(request, f"Заказ подтвержден")
    return redirect('profile')


@user_passes_test(lambda u: u.groups.filter(name='loader').exists())
def loader_order_approved(request, pk):
    order = Order.objects.get(pk=pk)
    order.step = 'весы-подтверждение'
    order.save()
    messages.success(request, f"Загрузка подтверждена")
    return redirect('profile')


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
                order.cycle_total = math.ceil(int(order.mass) / int(lifting_capacity))
            order.step = 'загрузка'
            order.save()
            messages.success(request, f"Заказ взвешен и подтвержден!")
            return redirect("order-detail", order.id)
    else:
        form = MeasureForm()
    return render(request, 'order_measurements.html', {'form': form})


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
            return redirect('profile')
    else:
        form = MeasureApprovedForm()
    return render(request, 'order_approved_measurements.html', {'form': form})


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
    return render(request, "fraction_price.html", {"form": form})


@user_passes_test(lambda u: u.groups.filter(name='security').exists())
def security_order_exit_approved(request, pk):
    order = Order.objects.get(pk=pk)
    order.status = 'выехал'
    order.step = 'охрана'
    order.cycle = int(order.cycle) - 1
    order.cycles_left = int(order.cycles_left) + 1
    if int(order.cycle) <= 0:
        order.step = 'завершен'
        order.status = 'завершен'
    order.save()
    messages.success(request, f"Выезд зазачика подтвержден")
    return redirect('security_approve_orders')


@user_passes_test(lambda u: u.is_superuser)
def download_check(request, file_id):
    file = get_object_or_404(Pay, pk=file_id)
    file_url = os.path.join('media', file.file.name)
    file_extension = os.path.splitext(file_url)[1].lower()
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    if file_extension in allowed_extensions:
        content_type = 'application/pdf' if file_extension == '.pdf' else 'image/*'
        response = FileResponse(open(file_url, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file.id}{file_extension}"'
        return response


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
    can.drawString(170, 181, str(order.mass))
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


def send_pay(request, user, pdf, mail_subject, message, order):
    # email_send = EmailMessage(mail_subject, message, attachments=[("paycheck.pdf", pdf,
    #                                                                'application/pdf')],
    #                           to=[user])
    send_pay_task.delay(user.email, pdf, mail_subject, message, order.id)
    # if email_send.send():
    messages.success(request, 'Заказ создан, счет на предоплату отправлен вам на почту!')
    # else:
    #     messages.error(request, f"Проблема отправки письма на {user.email},"
    #                                  f""f"Введите существующую почту!")
    #     return redirect("order-detail", order.id)
