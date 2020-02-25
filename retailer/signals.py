# Core Django imports
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

# Imports from my apps
from .models import Shipment
from .tasks import get_shipment, get_shipment_details, save_shipments, error_handler


@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    print('>>>> User have logged in ... <<<<<', user.email)
    get_shipment.delay(user.email)


@receiver(post_save, sender=Shipment)
def create_shipmet_details_task(sender, instance, created, **kwargs):
    if created:
        get_shipment_details.apply_async((instance.shipmentId, instance.retailer.email, instance.id),
                                         link=save_shipments.s(instance.retailer.email, instance.id),
                                         link_error=error_handler.s())
    else:
        print(">>> Shipment instance is not created successfully")
