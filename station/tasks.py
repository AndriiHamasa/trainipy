from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_order_email(user_email, order_id):

    subject = "Successfully purchased tickets"
    message = f"Your order with number {order_id} was successfully placed."

    send_mail(
        subject,
        message,
        f"Trainipy {settings.EMAIL_HOST_USER}",
        [user_email],
        fail_silently=False,
    )
