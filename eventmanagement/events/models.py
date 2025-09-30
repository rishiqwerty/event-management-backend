from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class EventType(models.TextChoices):
    CONCERT = "CONCERT", "Concert"
    CONFERENCE = "CONFERENCE", "Conference"
    WORKSHOP = "WORKSHOP", "Workshop"
    MEETUP = "MEETUP", "Meetup"
    OTHER = "OTHER", "Other"


class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    show_time = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    seats_remaining = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event_type = models.CharField(max_length=100, blank=True, choices=EventType.choices)

    class Meta:
        indexes = [
            models.Index(fields=['start_time']),
        ]

    def save(self, *args, **kwargs):
        if self.pk is None and self.seats_remaining is None:
            self.seats_remaining = self.capacity
        super().save(*args, **kwargs)

