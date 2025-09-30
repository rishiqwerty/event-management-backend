import threading
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from events.models import Event
from reservations.models import Reservation
from django.test import TransactionTestCase

User = get_user_model()


class ConcurrencyThreadTest(TransactionTestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass")
        self.user2 = User.objects.create_user(username="user2", password="pass")
        self.event = Event.objects.create(
            title="Thread Event", seats_remaining=1, organizer=self.user1,
            start_time="2030-01-01T10:00:00Z", end_time="2030-01-01T12:00:00Z", show_time="2030-01-01T09:00:00Z", capacity=1
        )
        self.url = reverse("reservation-list")

    def reserve(self, user, results, idx):
        client = APIClient()
        client.force_authenticate(user=user)
        payload = {"event_id": self.event.id}
        resp = client.post(self.url, payload, format="json")
        results[idx] = resp.status_code

    def test_threaded_reservations(self):
        results = {}
        t1 = threading.Thread(target=self.reserve, args=(self.user1, results, 1))
        t2 = threading.Thread(target=self.reserve, args=(self.user2, results, 2))

        t1.start(); t2.start()
        t1.join(); t2.join()
        print(results)
        self.assertTrue(
        Reservation.objects.count() <= 1,
            "Overbooking occurred!"
        )
        self.assertIn(201, results.values())
        self.assertIn(400, results.values())
        self.assertEqual(Reservation.objects.count(), 1)
