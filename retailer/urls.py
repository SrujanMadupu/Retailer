from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.auth_user import AuthUserView
from .views.shipments import ShipmentsView
from .views.retailer import RetailerViewSet

router = DefaultRouter()
router.register('users', RetailerViewSet)

urlpatterns = [
    path('shipments/', ShipmentsView.as_view()),
    path('login/', AuthUserView.as_view()),
    path('retailer/', include(router.urls)),
]
