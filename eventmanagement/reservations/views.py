from django.shortcuts import render
from .models import Event, Reservation
from rest_framework import viewsets, serializers
from .serializers import ReservationSerializer
from django.db import transaction
from django.db.models import F
import logging
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


class ReservationViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing reservations.
    Users can create reservations for events, ensuring that seat availability is respected.
    Users can only view and manage their own reservations.
    """

    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        event = serializer.validated_data["event_id"]
        try:
            with transaction.atomic():
                update = Event.objects.filter(
                    pk=event.pk, seats_remaining__gt=0
                ).update(seats_remaining=F("seats_remaining") - 1)
                if update == 0:
                    raise serializers.ValidationError(
                        "No seats remaining for this event."
                    )
                try:
                    serializer.save(user=self.request.user)
                except serializers.ValidationError as ve:
                    logger.warning(f"Validation error creating reservation: {ve}")
                    Event.objects.filter(pk=event.pk).update(
                        seats_remaining=F("seats_remaining") + 1
                    )
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error creating reservation: {e}")
                    Event.objects.filter(pk=event.pk).update(
                        seats_remaining=F("seats_remaining") + 1
                    )
                    raise serializers.ValidationError(
                        "An unexpected error occurred. Please try again."
                    )
        except serializers.ValidationError:
            raise
        except Exception as e:
            logger.error(f"Critical error in reservation creation: {e}")
            raise serializers.ValidationError(
                "Could not create reservation due to a server error."
            )

    def perform_destroy(self, instance):
        with transaction.atomic():
            event = Event.objects.select_for_update().get(pk=instance.event.pk)
            event.seats_remaining = F("seats_remaining") + 1
            event.save()
            instance.delete()

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        from rest_framework.response import Response

        return Response(
            {"detail": "PUT operation is not allowed."},
            status=405,
        )

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        from rest_framework.response import Response

        return Response(
            {"detail": "PATCH operation is not allowed."},
            status=405,
        )
