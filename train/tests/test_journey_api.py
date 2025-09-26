from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from train.models import Journey, Route, Station, Train, TrainType, Crew
from train.serializers import JourneyListSerializer, JourneyDetailSerializer


JOURNEY_URL = reverse("train:journey-list")


def sample_station(name="Kiev", latitude=50.45466, longitude=30.5238):
    return Station.objects.get_or_create(
        name=name,
        defaults={"latitude": latitude, "longitude": longitude}
    )[0]


def sample_train_type(name="Intercity"):
    return TrainType.objects.get_or_create(name=name)[0]


def sample_train(name="Rick", cargo_num=10, places_in_cargo=30, train_type=None):
    if not train_type:
        train_type = sample_train_type()
    return Train.objects.get_or_create(
        name=name,
        defaults={
            "cargo_num": cargo_num,
            "places_in_cargo": places_in_cargo,
            "train_type": train_type
        }
    )[0]


def sample_crew(first_name="Rubeus", last_name="Hagrid", position=Crew.Position.DRIVER):
    return Crew.objects.get_or_create(
        first_name=first_name,
        last_name=last_name,
        position=position
    )[0]


def sample_journey(**params):
    station_1 = sample_station(name="Kiev", latitude=50.45466, longitude=30.5238)
    station_2 = sample_station(name="Lviv", latitude=49.84768, longitude=24.0332)
    route = Route.objects.get_or_create(source=station_1, destination=station_2)[0]
    train = sample_train(
        cargo_num=15,
        places_in_cargo=25
    )
    crew = sample_crew()
    defaults = {
        "route": route,
        "train": train,
        "number_train": 725,
        "departure_time": "2025-06-02T14:00:00Z",
        "arrival_time": "2025-06-02T16:50:00Z",
        "status": "scheduled"
    }
    defaults.update(params)
    crew_members = defaults.pop("crew", [crew])
    journey = Journey.objects.create(**defaults)
    journey.crew.set(crew_members)
    return journey


def detail_url(journey_id):
    return reverse("train:journey-detail", args=[journey_id])


class UnauthenticatedJourneyApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_journey(self):
        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedJourneyApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@user.com",
            "userpass"
        )
        self.client.force_authenticate(self.user)
        self.journey = sample_journey()
        self.station_1 = sample_station("Rivne")
        self.station_2 = sample_station("Lviv")
        self.route = Route.objects.get_or_create(
            source=self.station_1,
            destination=self.station_2
        )[0]
        self.train = sample_train()
        self.crew = sample_crew()

    def test_journey_list(self):
        journey = sample_journey()
        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data["results"]
        self.assertTrue(any(j["id"] == journey.id for j in results))

    def test_journey_detail(self):
        url = detail_url(self.journey.id)
        res = self.client.get(url)
        serializer = JourneyDetailSerializer(self.journey)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_source_name(self):
        journey_1 = sample_journey()
        journey_2 = sample_journey(
            route=Route.objects.get_or_create(
                source=sample_station("Odessa", 46.4825, 30.7233),
                destination=sample_station("Lviv", 49.84768, 24.0332)
            )[0]
        )
        res = self.client.get(JOURNEY_URL, {"source_name": "Kiev"})
        results = res.data["results"]
        self.assertTrue(any(j["id"] == journey_1.id for j in results))
        self.assertFalse(any(j["id"] == journey_2.id for j in results))

    def test_filter_by_destination_name(self):
        journey_1 = sample_journey()
        journey_2 = sample_journey(
            route=Route.objects.get_or_create(
                source=sample_station("Kiev"),
                destination=sample_station("Odessa", 46.4825, 30.7233)
            )[0]
        )
        res = self.client.get(
            JOURNEY_URL,
            {"destination_name": "Lviv"}
        )
        results = res.data["results"]
        self.assertTrue(any(j["id"] == journey_1.id for j in results))
        self.assertFalse(any(j["id"] == journey_2.id for j in results))

    def test_filter_by_train_name(self):
        journey_1 = sample_journey()
        train_intercity = sample_train(
            name="Intercity C1",
            cargo_num=5,
            places_in_cargo=25
        )
        journey_2 = sample_journey(train=train_intercity)
        res = self.client.get(JOURNEY_URL, {"train_name": "Rick"})
        results = res.data["results"]
        self.assertTrue(any(j["id"] == journey_1.id for j in results))
        self.assertFalse(any(j["id"] == journey_2.id for j in results))

    def test_filter_by_departure_time(self):
        journey_1 = sample_journey(
            departure_time="2025-06-02T14:00:00Z"
        )
        journey_2 = sample_journey(
            departure_time="2025-06-03T14:00:00Z"
        )
        res = self.client.get(
            JOURNEY_URL,
            {"departure_time": "2025-06-02"}
        )
        results = res.data["results"]
        self.assertTrue(any(j["id"] == journey_1.id for j in results))
        self.assertFalse(any(j["id"] == journey_2.id for j in results))

    def test_filter_by_arrival_time(self):
        journey_1 = sample_journey(
            arrival_time="2025-06-02T16:50:00Z"
        )
        journey_2 = sample_journey(
            arrival_time="2025-06-03T16:50:00Z"
        )
        res = self.client.get(
            JOURNEY_URL,
            {"arrival_time": "2025-06-02"}
        )
        results = res.data["results"]
        self.assertTrue(any(j["id"] == journey_1.id for j in results))
        self.assertFalse(any(j["id"] == journey_2.id for j in results))

    def test_create_journey_forbidden(self):
        payload = {
            "route": self.route.id,
            "train": self.train.id,
            "crew": [self.crew.id],
            "number_train": 123,
            "departure_time": "2025-06-10T10:00:00Z",
            "arrival_time": "2025-06-10T12:00:00Z",
            "status": "scheduled"
        }
        res = self.client.post(JOURNEY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminJourneyApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            "admin@admin.com",
            "adminpass"
        )
        self.client.force_authenticate(self.admin)
        self.journey = sample_journey()

    def test_create_journey(self):
        station_1 = Station.objects.create(
            name="Ivano-Frankivsk",
            latitude=50.45466,
            longitude=30.5238
        )
        station_2 = Station.objects.create(
            name="Mariupol",
            latitude=49.84768,
            longitude=24.0332
        )
        route = Route.objects.create(
            source=station_1,
            destination=station_2
        )
        train_type = TrainType.objects.create(
            name="Intercity C2"
        )
        train = Train.objects.create(
            name="Morty",
            cargo_num=10,
            places_in_cargo=30,
            train_type=train_type
        )
        crew = Crew.objects.create(
            first_name="Rubeus",
            last_name="Hagrid",
            position=Crew.Position.DRIVER
        )
        payload = {
            "route": route.id,
            "train": train.id,
            "crew": crew.id,
            "number_train": 726,
            "departure_time": "2025-06-02T14:00:00Z",
            "arrival_time": "2025-06-02T16:50:00Z",
            "status": "scheduled"
        }
        res = self.client.post(JOURNEY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


    def test_full_update_journey(self):
        new_train = sample_train(name="Express")
        new_route = Route.objects.get_or_create(
            source=sample_station("Odessa", 46.4825, 30.7233),
            destination=sample_station("Kharkiv", 50.001, 36.25)
        )[0]
        payload = {
            "number_train": 999,
            "train": new_train.id,
            "route": new_route.id,
            "crew": [sample_crew().id],
            "departure_time": "2025-06-05T10:00:00Z",
            "arrival_time": "2025-06-05T15:00:00Z",
        }
        url = detail_url(self.journey.id)
        res = self.client.put(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.journey.refresh_from_db()
        self.assertEqual(self.journey.number_train, payload["number_train"])
        self.assertEqual(self.journey.train.id, payload["train"])
        self.assertEqual(self.journey.route.id, payload["route"])
        self.assertEqual(self.journey.departure_time.isoformat(), "2025-06-05T10:00:00+00:00")
        self.assertEqual(self.journey.arrival_time.isoformat(), "2025-06-05T15:00:00+00:00")

    def test_partial_update_journey(self):
        new_number_train = 888
        payload = {"number_train": new_number_train}
        url = detail_url(self.journey.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.journey.refresh_from_db()
        self.assertEqual(self.journey.number_train, new_number_train)
        self.assertEqual(self.journey.train.name, "Rick")
