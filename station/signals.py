from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .tasks import send_order_email

@receiver(post_save, sender=Order)
def send_email_on_order_creation(sender, instance, created, **kwargs):
    if created:
        send_order_email.delay(instance.user.email, instance.id)
