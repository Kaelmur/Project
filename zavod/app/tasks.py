from celery import shared_task
from django.core.mail import EmailMessage


@shared_task()
def send_pay_task(user, pdf, mail_subject, message, order):
    email_send = EmailMessage(mail_subject, message, attachments=[("paycheck.pdf", pdf,
                                                                   'application/pdf')],
                              to=[user])
    success = email_send.send()
    return success, user, order


@shared_task()
def verification(user, mail_subject, message):
    email_send = EmailMessage(mail_subject, message, to=[user])
    success = email_send.send()
    return success, user

