from .models import Event, Reservation
from rest_framework import serializers
from events.serializers import EventSerializer


class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    event = EventSerializer(read_only=True)  # nested output
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), write_only=True
    )  # for post ony

    class Meta:
        model = Reservation
        fields = ["id", "event", "event_id", "user", "created_at"]
        read_only_fields = ["id", "user", "event", "created_at"]

    def validate(self, attrs):
        user = self.context['request'].user
        event = attrs.get("event_id")

        if Reservation.objects.filter(user=user, event=event).exists():
            raise serializers.ValidationError("You have already made a reservation for this event.")
        if event.seats_remaining <= 0:
            raise serializers.ValidationError("No seats remaining for this event.")
        return attrs

    def create(self, validated_data):
        return Reservation.objects.create(
            user=self.context['request'].user,
            event=validated_data["event_id"]
        )
