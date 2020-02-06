from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.auth_user import AuthUserView
from .views.shipments import ShipmentViewSet
from .views.api_queue import ShipmentAPIView
from .views.retailer import RetailerViewSet, RetailerAPIView

router = DefaultRouter()
router.register('retailers', RetailerViewSet)
router.register('shipments', ShipmentViewSet)

urlpatterns = [
    path('login/', AuthUserView.as_view()),
    path('shipment/', ShipmentAPIView.as_view()),
    path('router/', include(router.urls)),
]
