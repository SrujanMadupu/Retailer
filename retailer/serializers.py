# Third-party app imports
from rest_framework import serializers

# Imports from my apps
from .models import Retailer, Shipment, ShipmentItem, Transport, CustomerDetails, BillingDetails


class RetailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retailer
        fields = '__all__'
        extra_kwargs = {
            'client_id': {'write_only': True},
            'client_secret': {'write_only': True},
            'password': {'write_only': True}
        }


class ShipmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentItem
        fields = '__all__'


class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = '__all__'


class ShipmentSerializer(serializers.ModelSerializer):
    retailer_name = serializers.CharField(source='retailer.name', read_only=True)
    shipment_items = ShipmentItemSerializer(source='shipmentitems', many=True, read_only=True)
    shipment_transport = TransportSerializer(source='transport', read_only=True)

    class Meta:
        model = Shipment
        fields = ('retailer_name', 'shipmentId', 'shipmentDate', 'shipmentReference', 'shipment_items',
                  'shipment_transport', 'retailer')
        extra_fields = {
            'retailer': {'write_only': True}
        }


class CustomerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetails
        fields = '__all__'


class BillingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingDetails
        fields = '__all__'

