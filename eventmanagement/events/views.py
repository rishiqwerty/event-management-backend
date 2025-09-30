from rest_framework import viewsets, permissions
from .models import Event
from .serializers import EventSerializer
from reservations.models import Reservation
from reservations.serializers import ReservationSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user


class EventViewSet(viewsets.ModelViewSet):
    """
    API for managing events.
    Only the organizer can create, update, or delete events.
    Anyone can view the list of events and event details.
    Only the organizer can view all reservations for their events.
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=["get"], url_path="total-reservations")
    def reservations(self, request, pk=None):
        """
        Retrieve the total number of reservations for the event.
        Only the organizer can access this endpoint.
        """
        event = self.get_object()
        if event.organizer != request.user:
            return Response(
                {"detail": "Not authorized to access this event reservations details."},
                status=403,
            )
        reservations = Reservation.objects.filter(event=event)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)
