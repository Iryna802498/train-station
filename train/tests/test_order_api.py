from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from train.models import Order, Ticket
from .test_journey_api import sample_journey


ORDER_URL = reverse("train:order-list")


def sample_order(user, journey=None):
    if not journey:
        journey = sample_journey()
    order = Order.objects.create(user=user)
    Ticket.objects.create(
        order=order,
        journey=journey,
        cargo=3,
        seat=5
    )
    return order


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_order(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_orders_only_for_current_user(self):
        other_user = get_user_model().objects.create_user(
            "other@test.com",
            "pass123"
        )
        order1 = sample_order(self.user)
        order2 = sample_order(other_user)
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(order1.id, [o["id"] for o in res.data["results"]])
        self.assertNotIn(order2.id, [o["id"] for o in res.data["results"]])

    def test_create_order(self):
        journey = sample_journey()
        payload = {
            "tickets": [
                {
                    "journey": journey.id,
                    "cargo": 1,
                    "seat": 5,
                }
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)
        self.assertEqual(
            res.data["tickets"][0]["journey"],
            journey.id
        )
        self.assertEqual(res.data["tickets"][0]["cargo"], 1)
        self.assertEqual(res.data["tickets"][0]["seat"], 5)
