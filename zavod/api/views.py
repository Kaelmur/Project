from rest_framework import generics, permissions
from app.models import Order, FractionPrice
from django.utils import timezone
from django.core.mail import EmailMessage
from rest_framework import serializers
from .serializers import OrderSerializer
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
import io


class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
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
                print('Заказ создан, счет на предоплату отправлен вам на почту!')
            else:
                print(f"Problem sending email to {user.email}, please check if you typed it correctly")
                order.delete()  # Rollback the order creation if email sending fails
                raise serializers.ValidationError(
                    f"Problem sending email to {user.email}, please check if you typed it correctly")
        else:
            order.status = "оплачен"
            order.save()
            print(f"Order activated")


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
