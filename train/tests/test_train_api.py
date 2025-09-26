from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from train.models import Train, TrainType
from train.serializers import TrainListSerializer, TrainDetailSerializer


TRAIN_URL = reverse("train:train-list")


def sample_train_type(name="Intercity"):
    return TrainType.objects.get_or_create(name=name)[0]


def sample_train(**params):
    train_type = params.pop("train_type", sample_train_type())
    defaults = {
        "name": "Hogwarts Express",
        "cargo_num": 10,
        "places_in_cargo": 30,
        "train_type": train_type
    }
    defaults.update(params)
    return Train.objects.get_or_create(
        name=defaults["name"],
        defaults=defaults
    )[0]


def train_detail_url(train_id):
    return reverse("train:train-detail", args=[train_id])


class UnauthenticatedTrainApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_train(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@user.com",
            "userpass"
        )
        self.client.force_authenticate(self.user)
        self.train = sample_train()
        self.train_type = sample_train_type()

    def test_train_list(self):
        self.train
        res = self.client.get(TRAIN_URL)
        trains = Train.objects.order_by("id")
        serializer = TrainListSerializer(trains, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_train_detail(self):
        url = train_detail_url(self.train.id)
        res = self.client.get(url)
        serializer = TrainDetailSerializer(self.train)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_train_create_forbidden(self):
        payload = {
            "name": "Hogwarts",
            "cargo_num": 10,
            "places_in_cargo": 30,
            "train_type": self.train_type.id
        }
        res = self.client.post(TRAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            "admin@admin.com",
            "adminpass"
        )
        self.client.force_authenticate(self.admin)
        self.train_type = sample_train_type()

    def test_create_train(self):
        payload = {
            "name": "Hogwarts",
            "cargo_num": 10,
            "places_in_cargo": 30,
            "train_type": self.train_type.id
        }
        res = self.client.post(TRAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
