from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from reservations.models import Reservation
from events.models import Event

User = get_user_model()


class ReservationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.event = Event.objects.create(
            organizer=self.user,
            title='Test Event',
            start_time='2030-01-01T10:00:00Z',
            end_time='2030-01-01T12:00:00Z',
            show_time='2030-01-01T09:00:00Z',
            capacity=2,
            seats_remaining=2,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_reservation_decrements_seats(self):
        url = reverse('reservation-list')
        response = self.client.post(url, {'event_id': self.event.id})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.event.refresh_from_db()
        self.assertEqual(self.event.seats_remaining, 1)

    def test_duplicate_reservation_not_allowed(self):
        url = reverse('reservation-list')
        self.client.post(url, {'event_id': self.event.id})
        response = self.client.post(url, {'event_id': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You have already made a reservation for this event.', str(response.data))

    def test_delete_reservation_increments_seats(self):
        reservation = Reservation.objects.create(user=self.user, event=self.event)
        self.event.seats_remaining = 1
        self.event.save()
        url = reverse('reservation-detail', args=[reservation.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.event.refresh_from_db()
        self.assertEqual(self.event.seats_remaining, 2)

    def test_users_trying_to_book_last_ticket(self):
        user2 = User.objects.create_user(username='testuser2', password='testpass2')
        self.event.seats_remaining = 1
        self.event.save()
        url = reverse('reservation-list')

        self.client.force_authenticate(user=self.user)
        response1 = self.client.post(url, {'event_id': self.event.id})
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Second user tries to book last ticket
        self.client.force_authenticate(user=user2)
        response2 = self.client.post(url, {'event_id': self.event.id})
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        # Third user tries to book (should fail)
        user3 = User.objects.create_user(username='testuser3', password='testpass3')
        self.client.force_authenticate(user=user3)
        response3 = self.client.post(url, {'event_id': self.event.id})
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

        self.event.refresh_from_db()
        self.assertEqual(self.event.seats_remaining, 0)
