from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from train.models import Crew
from train.serializers import CrewSerializer


CREW_URL = reverse("train:crew-list")


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_crew(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_crew_list(self):
        Crew.objects.create(
            first_name="Hans",
            last_name="Landa",
            position=Crew.Position.ASSISTANT_DRIVER
        )
        Crew.objects.create(
            first_name="Shoshanna",
            last_name="Dreyfus",
            position=Crew.Position.TRAIN_MANAGER
        )
        res = self.client.get(CREW_URL)
        crews = Crew.objects.order_by("id")
        serializer = CrewSerializer(crews, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "Travis",
            "last_name": "Scott",
            "position": Crew.Position.ASSISTANT_DRIVER
        }
        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            "admin@admin.com",
            "adminpass"
        )
        self.client.force_authenticate(self.admin)

    def test_create_crew(self):
        payload = {
            "first_name":"Abel",
            "last_name":"Tesfaye",
            "position":Crew.Position.DRIVER
        }
        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
