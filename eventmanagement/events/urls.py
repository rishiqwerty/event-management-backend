from .views import EventViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'events', EventViewSet)

urlpatterns = [
    path("", include(router.urls)),
]