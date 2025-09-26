from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from train.models import Station
from train.serializers import StationSerializer


STATION_URL = reverse("train:station-list")


class UnauthenticatedStationApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_station(self):
        res = self.client.get(STATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_station_list(self):
        Station.objects.create(
            name="Kiev",
            latitude=50.45466,
            longitude=30.5238
        )
        res = self.client.get(STATION_URL)
        stations = Station.objects.order_by("id")
        serializer = StationSerializer(stations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_station_forbidden(self):
        payload = {
            "name": "Kiev",
            "latitude": 50.45466,
            "longitude": 30.5238
        }
        res = self.client.post(STATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminStationApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            "admin@example.admin",
            "adminpass"
        )
        self.client.force_authenticate(self.admin)

    def test_create_station(self):
        payload = {
            "name": "Kherson",
            "latitude": 46.65581,
            "longitude": 32.6178
        }
        res = self.client.post(STATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
