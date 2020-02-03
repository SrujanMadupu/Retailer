from rest_framework.throttling import UserRateThrottle


class ShipmentRateThrottle(UserRateThrottle):
    scope = 'shipment'


