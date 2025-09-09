from rest_framework import serializers
from .models import Station, TrainType


class StationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Station
        fields = (
            "id",
            "name",
            "latitude",
            "longitude"
        )


class TrainTypeSerializers(serializers.ModelSerializer):

    class Meta:
        model = TrainType
        fields = (
            "id",
            "name",
            "image"
        )
