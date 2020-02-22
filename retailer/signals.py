from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AuthUser, Shipment


@receiver(post_save, sender=AuthUser)
def fetch_shipments_task(sender, instance, created, **kwargs):
    """
    here do we do fetch all shipments for each method [FBR, FBB]
    create Shipment object
    """
    pass


@receiver(post_save, sender=Shipment)
def fetch_shipment_details_task(sender, instance, created, **kwargs):
    """
    When a Shipment is created, we take it's shipmentID and fetch it's details
    we get shipmentItems,  Transport, CustomerDetails, BillingDetails
    create objects for all
    """
    pass

