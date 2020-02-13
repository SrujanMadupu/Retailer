from rest_framework import serializers
from .models import Retailer, Shipment, ShipmentItem, Transport, CustomerDetails, BillingDetails


class RetailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retailer
        fields = ('id', 'name', 'email')


class ShipmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentItem
        fields = ('id', 'orderItemId', 'orderId', 'orderDate', 'latestDeliveryDate', 'ean',
                  'title', 'quantity', 'offerPrice', 'offerCondition', 'fulfilmentMethod',
                  'shipment')

    def create(self, validated_data):
        return ShipmentItem.objects.create(**validated_data)

    def validate(self, attrs):
        print(">>> attrs", attrs)
        return attrs


class ShipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipment
        fields = ('id', 'shipmentId', 'shipmentDate', 'shipmentReference', 'retailer')

    def create(self, validated_data):
        return Shipment.objects.create(**validated_data)

    def validate(self, attrs):
        print(">>> attrs", attrs)
        return attrs


class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = ('id', 'transportId', 'transporterCode', 'trackAndTrace', 'shipment')

    def create(self, validated_data):
        return Transport.objects.create(**validated_data)

    def validate(self, attrs):
        print(">>> attrs", attrs)
        return attrs


class CustomerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetails
        fields = ('id', 'salutationCode', 'firstName', 'surname', 'streetName',
                  'houseNumber', 'zipCode', 'city', 'countryCode', 'email', 'company',
                  'houseNumberExtended', 'shipment')

    def create(self, validated_data):
        return CustomerDetails.objects.create(**validated_data)

    def validate(self, attrs):
        return attrs


class BillingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingDetails
        fields = ('id', 'salutationCode', 'firstName', 'surname', 'streetName',
                  'houseNumber', 'zipCode', 'city', 'countryCode', 'email', 'shipment')

    def create(self, validated_data):
        return BillingDetails.objects.create(**validated_data)

    def validate(self, attrs):
        return attrs

