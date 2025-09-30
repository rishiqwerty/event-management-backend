from .views import ReservationViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'reservations', ReservationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
