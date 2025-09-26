from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from train.models import Station, Route
from train.serializers import RouteListSerializer, RouteDetailSerializer


ROUTE_URL = reverse("train:route-list")


def sample_station(name="Kiev", latitude=50.45466, longitude=30.5238):
    return Station.objects.get_or_create(
        name=name,
        defaults={"latitude": latitude, "longitude": longitude}
    )[0]


def sample_route(source=None, destination=None):
    if not source:
        source = sample_station(name="Odessa", latitude=42.15244, longitude=30.1237)
    if not destination:
        destination = sample_station(name="Kiev", latitude=50.45466, longitude=30.5238)
    return Route.objects.get_or_create(source=source, destination=destination)[0]


def detail_url(route_id):
    return reverse("train:route-detail", args=[route_id])


class UnauthenticatedRouteApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_route(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)
        self.route = sample_route()

    def test_route_list(self):
        self.route
        res = self.client.get(ROUTE_URL)
        routers = Route.objects.order_by("id")
        serializer = RouteListSerializer(routers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_route_detail(self):
        url = detail_url(self.route.id)
        res = self.client.get(url)
        serializer = RouteDetailSerializer(self.route)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        source = sample_station(name="Source")
        destination = sample_station(name="Destination")
        payload = {
            "source": source.id,
            "destination": destination.id
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            "admin@admin.com",
            "adminpass"
        )
        self.client.force_authenticate(self.admin)
        self.station = sample_station()
        self.route = sample_route()

    def test_route_create(self):
        destination = sample_station(
            name="Lviv",
            latitude=49.84295,
            longitude=24.0311
        )
        payload = {
            "source": self.station.id,
            "destination": destination.id
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
