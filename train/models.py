import os
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


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
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

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

