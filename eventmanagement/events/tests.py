from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from events.models import Event
from reservations.models import Reservation
from django.contrib.auth import get_user_model

User = get_user_model()


class EventAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.organizer = User.objects.create_user(
            username="organizer", password="pass123"
        )
        self.user = User.objects.create_user(username="user", password="pass123")
        self.event = Event.objects.create(
            title="Test Event",
            description="Test event Description",
            seats_remaining=10,
            organizer=self.organizer,
            start_time="2030-01-01T10:00:00Z",
            end_time="2030-01-01T12:00:00Z",
            show_time="2030-01-01T09:00:00Z",
            capacity=10,
        )

    def test_event_list(self):
        """Anyone can list events."""
        url = reverse("event-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["results"][0]["title"], "Test Event")

    def test_create_event(self):
        url = reverse("event-list")
        payload = {
            "title": "Hackathon",
            "description": "Code .",
            "seats_remaining": 5,
            "show_time": "2030-05-01T09:00:00Z",
            "start_time": "2030-05-01T10:00:00Z",
            "end_time": "2030-05-01T12:00:00Z",
            "capacity": 5,
        }

        self.client.force_authenticate(user=self.user)
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["organizer"], self.user.id)

    def test_only_organizer_can_update_event(self):
        url = reverse("event-detail", args=[self.event.id])

        # user
        self.client.force_authenticate(user=self.user)
        resp = self.client.patch(url, {"title": "Updated Name"}, format="json")
        self.assertEqual(resp.status_code, 403)

        # Organizer
        self.client.force_authenticate(user=self.organizer)
        resp = self.client.patch(url, {"title": "Updated Name"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["title"], "Updated Name")

    def test_only_organizer_can_view_reservations(self):
        Reservation.objects.create(user=self.user, event=self.event)
        url = reverse("event-reservations", args=[self.event.id])

        # user
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

        # Organizer
        self.client.force_authenticate(user=self.organizer)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["user"], str(self.user))
