from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.auth_user import AuthUserView
from .views.shipments import ShipmentViewSet
from .views.retailer import RetailerViewSet

router = DefaultRouter()
router.register('retailers', RetailerViewSet)
router.register('shipments', ShipmentViewSet)

urlpatterns = [
    path('login/', AuthUserView.as_view()),
    path('', include(router.urls)),
]
