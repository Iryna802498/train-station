import os
import uuid
from math import radians, sin, cos, sqrt, asin
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from train_station import settings


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )

    def __str__(self) -> str:
        return self.name


def train_type_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/trains/", filename)


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(
        null=True,
        upload_to=train_type_image_file_path
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Crew(models.Model):
    class Position(models.TextChoices):
        DRIVER = "driver", "Driver"
        ASSISTANT_DRIVER = "assistant driver", "Assistant driver"
        CONDUCTOR = "conductor", "Conductor"
        SENIOR_CONDUCTOR = "senior conductor", "Senior conductor"
        TRAIN_MANAGER = "train manager", "Train manager"
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = models.CharField(
        max_length=20,
        choices=Position.choices
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


def calculate_distance(
        source_latitude: float,
        source_longitude: float,
        destination_latitude: float,
        destination_longitude: float
    ) -> int:
    earth_radius = 6371
    delta_lat = radians(destination_latitude - source_latitude)
    delta_lon = radians(destination_longitude - source_longitude)
    haversine_formula = (
        sin(delta_lat / 2) ** 2 + cos(radians(source_latitude))
        * cos(radians(destination_latitude)) * sin(delta_lon / 2) ** 2)
    central_angle = 2 * asin(sqrt(haversine_formula))
    distance = round(earth_radius * central_angle)
    return distance


class Route(models.Model):
    source = models.ForeignKey(
        Station,
        related_name="routes_from",
        on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Station,
        related_name="routes_to",
        on_delete=models.CASCADE
    )
    distance = models.PositiveIntegerField(editable=False)

    def save(self, *args, **kwargs):
        if self.source and self.destination:
            self.distance = calculate_distance(
                self.source.latitude, self.source.longitude,
                self.destination.latitude, self.destination.longitude
            )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.source.name} -> {self.destination.name} "
            f"{self.distance} km"
        )


class Train(models.Model):
    name = models.CharField(max_length=255, unique=True)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType,
        related_name="trains",
        on_delete=models.CASCADE
    )

    @property
    def total_places(self) -> int:
        return self.cargo_num * self.places_in_cargo

    def __str__(self) -> str:
        return self.name


class Journey(models.Model):
    route = models.ForeignKey(
        Route,
        related_name="journeys",
        on_delete=models.CASCADE
    )
    train = models.ForeignKey(
        Train,
        related_name="journeys",
        on_delete=models.CASCADE
    )
    crew = models.ManyToManyField(Crew, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self) -> str:
        return (
            f"{self.route.source.name} -> "
            f"{self.route.destination.name} "
            f"at {self.departure_time}"
        )

    class Meta:
        ordering = ["-departure_time"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="orders",
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey,
        related_name="tickets",
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            max_value = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= max_value):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {train_attr_name}): "
                        f"(1, {max_value})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.journey.train.name} (cargo: {self.cargo}, seat: {self.seat})"
        )

    class Meta:
        unique_together = ("train", "cargo", "seat")
        ordering = ["cargo", "seat"]
