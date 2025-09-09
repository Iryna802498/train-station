from rest_framework import serializers
from .models import Station, TrainType, Crew


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


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "position"
        )
