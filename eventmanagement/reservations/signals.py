from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Reservation


@receiver(post_save, sender=Reservation)
def decrease_seats_remaining(sender, instance, created, **kwargs):
    print("Reservation created signal triggered")
    if created:
        event = instance.event
        print(f"Event before decrement: {event.seats_remaining} seats remaining")
        if event.seats_remaining > 0:
            event.seats_remaining = event.capacity - event.reservations.count()
            event.save()

@receiver(post_delete, sender=Reservation)
def increase_seats_remaining(sender, instance, **kwargs):
    print("Reservation deleted signal triggered")
    event = instance.event
    event.seats_remaining = event.capacity - event.reservations.count()
    event.save()
