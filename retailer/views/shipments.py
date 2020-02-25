# Stdlib imports

# Core Django imports
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Third-party app imports
from rest_framework.viewsets import ModelViewSet

# Imports from my apps
from ..models import Shipment
from ..throttles import ShipmentRateThrottle
from ..serializers import ShipmentSerializer


class ShipmentViewSet(ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    throttle_classes = [ShipmentRateThrottle]

    @method_decorator(login_required)
    def list(self, request, *args, **kwargs):
        return super().list(request)
