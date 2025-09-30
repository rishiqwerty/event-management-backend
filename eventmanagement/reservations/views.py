from django.shortcuts import render
from .models import Event, Reservation
from rest_framework import viewsets, serializers
from .serializers import ReservationSerializer
from django.db import transaction
from django.db.models import F


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        event = serializer.validated_data["event_id"]
        with transaction.atomic():
            update = Event.objects.filter(
                pk=event.pk,
                seats_remaining__gt=0
            ).update(seats_remaining=F('seats_remaining') - 1)
            if update == 0:
                raise serializers.ValidationError("No seats remaining for this event.")
            try:
                serializer.save(user=self.request.user)
            except Exception as e:
                print(e)
                Event.objects.filter(pk=event.pk).update(seats_remaining=F('seats_remaining') + 1)

                raise e
