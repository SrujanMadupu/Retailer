from django.db import models


# Create your models here.
class Retailer(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=10)
    client_id = models.CharField(max_length=50)
    client_secret = models.CharField(max_length=100)

    def __str__(self):
        return "{0} {1}".format(self.name, self.email)


class Shipment(models.Model):
    shipmentId = models.IntegerField()
    shipmentDate = models.DateTimeField()
    shipmentReference = models.CharField(max_length=25, default="")
    retailer = models.ForeignKey('Retailer', related_name='shipments', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.shipmentId)


class ShipmentItem(models.Model):
    orderItemId = models.CharField(max_length=50)
    orderId = models.CharField(max_length=35)
    orderDate = models.DateTimeField()
    latestDeliveryDate = models.DateTimeField()
    ean = models.CharField(max_length=35)
    title = models.TextField()
    quantity = models.IntegerField()
    offerPrice = models.DecimalField(max_digits=5, decimal_places=2)
    offerCondition = models.CharField(max_length=10)
    fulfilmentMethod = models.CharField(max_length=3)
    shipment = models.ForeignKey('Shipment', related_name='shipmentitems', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.orderItemId)


class Transport(models.Model):
    transportId = models.IntegerField()
    transporterCode = models.CharField(max_length=10)
    trackAndTrace = models.CharField(max_length=10)
    shipment = models.OneToOneField('Shipment', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.transportId)


class CustomerDetails(models.Model):
    salutationCode = models.CharField(max_length=5)
    firstName = models.CharField(max_length=35)
    surname = models.CharField(max_length=35)
    streetName = models.CharField(max_length=30)
    houseNumber = models.CharField(max_length=10)
    zipCode = models.CharField(max_length=10)
    city = models.CharField(max_length=30)
    countryCode = models.CharField(max_length=5)
    email = models.EmailField()
    company = models.CharField(max_length=35, default="")
    houseNumberExtended = models.CharField(max_length=50, default="")
    shipment = models.OneToOneField('Shipment', on_delete=models.CASCADE)

    def __str__(self):
        return "{0} {1}".format(self.firstName, self.surname)


class BillingDetails(models.Model):
    salutationCode = models.CharField(max_length=5)
    firstName = models.CharField(max_length=35)
    surname = models.CharField(max_length=35)
    streetName = models.CharField(max_length=30)
    houseNumber = models.CharField(max_length=10)
    zipCode = models.CharField(max_length=10)
    city = models.CharField(max_length=30)
    countryCode = models.CharField(max_length=5)
    email = models.EmailField()
    shipment = models.OneToOneField('Shipment', on_delete=models.CASCADE)

    def __str__(self):
        return "{0} {1}".format(self.firstName, self.surname)


class AuthUser(models.Model):
    email = models.EmailField()
    logged_in = models.DateTimeField()
    logged_out = models.DateTimeField(default="")

    def __str__(self):
        return "{0} {1}".fromat(self.email, self.logged_in)