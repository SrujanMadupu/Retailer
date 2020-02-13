from django.db.models import Manager


class ShipmentManager(Manager):
    def create(self, **kwargs):
        print(">>>> data received in manager", kwargs)
        obj_shipment = self.model(
            shipmentId=kwargs.get('shipmentId', ""),
            shipmentDate=kwargs.get('shipmentDate', ""),
            shipmentReference=kwargs.get('shipmentReference', ""),
            retailer=kwargs.get('retailer')
        )
        obj_shipment.save()
        return obj_shipment


class ShipmentItemManager(Manager):
    def create(self, **kwargs):
        print(">>>> data received in shipment item manager", kwargs)
        obj_shipment_item = self.model(
            orderItemId=kwargs.get('orderItemId', ''),
            orderId=kwargs.get('orderId', ''),
            orderDate=kwargs.get('orderDate', ''),
            latestDeliveryDate=kwargs.get('latestDeliveryDate', ''),
            ean=kwargs.get('ean', ''),
            title=kwargs.get('title', ''),
            quantity=kwargs.get('quantity', ''),
            offerPrice=kwargs.get('offerPrice', ''),
            offerCondition=kwargs.get('offerCondition', ''),
            fulfilmentMethod=kwargs.get('fulfilmentMethod', ''),
            shipment=kwargs.get('shipment')
        )
        obj_shipment_item.save()
        return obj_shipment_item


class TransportManager(Manager):
    def create(self, **kwargs):
        print(">>> data received in transport manager", kwargs)
        obj_transport = self.model(
            transportId=kwargs.get('transportId', ''),
            transporterCode=kwargs.get('transporterCode', ''),
            trackAndTrace=kwargs.get('trackAndTrace', ''),
            shipment=kwargs.get('shipment')
        )
        obj_transport.save()
        return obj_transport


class CustomerDetailsManager(Manager):
    def create(self, **kwargs):
        print(">>> data received in customer details manager", kwargs)
        obj_customer_details = self.model(
            salutationCode=kwargs.get('salutationCode', ''),
            firstName=kwargs.get('firstName', ''),
            surname=kwargs.get('surname', ''),
            streetName=kwargs.get('streetName', ''),
            houseNumber=kwargs.get('houseNumber', ''),
            zipCode=kwargs.get('zipCode', ''),
            city=kwargs.get('city', ''),
            countryCode=kwargs.get('countryCode', ''),
            email=kwargs.get('email', ''),
            company=kwargs.get('company', ''),
            houseNumberExtended=kwargs.get('houseNumberExtended', ''),
            shipment=kwargs.get('shipment', '')
        )
        obj_customer_details.save()
        return obj_customer_details


class BillingDetailsManager(Manager):
    def create(self, **kwargs):
        print(">>> data received in billing details manager", kwargs)
        obj_billing_details = self.model(
            salutationCode=kwargs.get('salutationCode', ''),
            firstName=kwargs.get('firstName', ''),
            surname=kwargs.get('surname', ''),
            streetName=kwargs.get('streetName', ''),
            houseNumber=kwargs.get('houseNumber', ''),
            zipCode=kwargs.get('zipCode', ''),
            city=kwargs.get('city', ''),
            countryCode=kwargs.get('countryCode', ''),
            email=kwargs.get('email', ''),
            shipment=kwargs.get('shipment', '')
        )
        obj_billing_details.save()
        return obj_billing_details

