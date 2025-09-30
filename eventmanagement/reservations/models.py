# models.py
from django.db import models
from django.conf import settings
from events.models import Event

User = settings.AUTH_USER_MODEL


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="reservations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')
        indexes = [models.Index(fields=['event'])]
