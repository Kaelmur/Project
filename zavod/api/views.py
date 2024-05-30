from rest_framework import generics, permissions
from rest_framework.views import APIView
from app.models import Order, FractionPrice, Pay
from django.utils import timezone
from django.core.mail import EmailMessage
from rest_framework import serializers
from .serializers import OrderSerializer, UserLoginSerializer, UserRegisterSerializer, OrderCreateSerializer, PaySerializer
from PyPDF2 import PdfWriter, PdfReader
from rest_framework.response import Response
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from rest_framework import status
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from users.models import UserManage as CustomUser
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import Group
from reportlab.lib.pagesizes import A4
from django.db.models import Q
import io


def user_belongs_to_security_group(user):
    security_group = Group.objects.get(name='security')
    return security_group in user.groups.all()


def user_belongs_to_loader_group(user):
    loader_group = Group.objects.get(name='loader')
    return loader_group in user.groups.all()


class IsSecurityGroup(permissions.BasePermission):
    message = 'User does not belong to the security group'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            user = CustomUser.objects.get(id=request.user.id)
            return user_belongs_to_security_group(user)
        return False


class IsOwnerOrSuperuser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user.is_superuser


class PaidOrderListView(generics.ListAPIView):
    queryset = Order.objects.filter(status='модерация').order_by("-date_ordered")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get']


class SecurityApproveOrderListView(generics.ListAPIView):
    queryset = Order.objects.filter(step='охрана-выход').order_by("-date_ordered")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsSecurityGroup]
    http_method_names = ['get']


class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    paginate_by = 5
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            queryset = Order.objects.exclude(status='неоплачено').order_by("-date_ordered")
            return queryset
        elif user.groups.filter(name='security').exists():
            return Order.objects.filter(Q(status='оплачен') | Q(status='выехал')).order_by("-date_ordered")
        elif user.groups.filter(name='loader').exists():
            return Order.objects.filter(step='загрузка').order_by("-date_ordered")
        else:
            return Order.objects.filter(user=self.request.user).order_by("-date_ordered")


class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = PaySerializer(data=request.data)
        if serializer.is_valid():
            file = Pay(file=request.FILES.get('file'), order=order)
            file.save()
            order.status = 'модерация'
            order.save()
            return Response({'detail': 'Чек принят. Ждите подтверждения'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']

    def perform_create(self, serializer):
        user = self.request.user
        mass = serializer.validated_data['mass']
        buyer = serializer.validated_data['buyer']
        fraction = serializer.validated_data['fraction']
        date_reserved = serializer.validated_data['date_reserved']

        local_time = timezone.localtime(date_reserved)
        serializer.validated_data['date_reserved'] = local_time

        fractions_price = FractionPrice.objects.get(fraction=fraction)
        price_without_nds = mass * float(fractions_price.price)
        price_nds = price_without_nds * 0.12
        total_price = price_without_nds + price_nds

        order = serializer.save(user=user, price=total_price)

        if buyer == "юр.лицо":
            mail_subject = f"Оплата заказа #{order.id}"
            message = "Check pdf file below to checkout"
            pdf = pdf_create(order, fractions_price, total_price, price_without_nds, price_nds)
            email_send = EmailMessage(mail_subject, message, attachments=[("paycheck.pdf", pdf, 'application/pdf')],
                                      to=[user.email])
            if email_send.send():
                Response({'Заказ создан, счет на предоплату отправлен вам на почту!'}, status=status.HTTP_200_OK)
            else:
                order.delete()
                raise serializers.ValidationError(
                    f"Problem sending email to {user.email}, please check if you typed it correctly")
        else:
            order.status = "оплачен"
            order.save()
            Response({"Order activated"}, status=status.HTTP_200_OK)


class RegisterUserView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)
            self.activate_email(request, user)
            return Response({'detail': 'Verification email sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def activate_email(self, request, user):
        token = default_token_generator.make_token(user)
        mail_subject = 'Verify your email'
        message = render_to_string('api_template_activate_email.html', {
            'user': user,
            "domain": get_current_site(request).domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": token,
            "protocol": "https" if request.is_secure() else "http",
        })
        email_send = EmailMessage(mail_subject, message, to=[user.email])
        if email_send.send():
            return True
        else:
            return False


class ActivateEmail(APIView):

    permission_classes = [permissions.AllowAny]

    def get(self, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except:
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            refresh = RefreshToken.for_user(user)
            user.email_verified = True
            user.save()
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {'id': user.id, 'username': user.username, 'mail': user.email, 'iin': user.iin,
                         'address_index': user.address_index, 'email_verified': user.email_verified}},
                status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid verification link'}, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['mail']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                self.send_verification_email(request, user)
                return Response({'detail': 'Verification email sent.'}, status=status.HTTP_200_OK)
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, request, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        current_site = get_current_site(request)
        mail_subject = "Log in"
        protocol = 'https' if request.is_secure() else 'http'
        domain = current_site.domain
        message = render_to_string('api_verification_email.html', {
            'user': user,
            'domain': domain,
            'uid': uid,
            'token': token,
            'protocol': protocol,
        })
        email_send = EmailMessage(mail_subject, message, to=[user.email])
        if email_send.send():
            return True
        else:
            return False


class VerifyEmailView(APIView):

    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except:
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            refresh = RefreshToken.for_user(user)
            user.email_verified = True
            user.save()
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {'id': user.id, 'username': user.username, 'mail': user.email, 'iin': user.iin, 'address_index': user.address_index, 'email_verified': user.email_verified}}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid verification link'}, status=status.HTTP_400_BAD_REQUEST)


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
    can.drawString(170, 181, str(float(order.mass)))
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


class SecurityOrderExitApprovedView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSecurityGroup]

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        order.status = 'выехал'
        order.step = 'охрана'
        order.cycle = int(order.cycle) - 1
        order.cycles_left = int(order.cycles_left) + 1
        if int(order.cycle) <= 0:
            order.step = 'завершен'
            order.status = 'завершен'
        order.save()
        return Response({'detail': 'Выезд зазачика подтвержден'}, status=status.HTTP_200_OK)


class ActivateOrder(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        order.status = "оплачен"
        order.save()
        return Response({'detail': 'Заказ активирован'}, status=status.HTTP_200_OK)
