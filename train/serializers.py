from rest_framework import serializers
from .models import Station, TrainType, Crew, Route


class StationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Station
        fields = (
            "id",
            "name",
            "latitude",
            "longitude"
        )


class TrainTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainType
        fields = (
            "id",
            "name",
            "image"
        )


class TrainTypeImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainType
        fields = (
            "id",
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


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance"
        )


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance"
        )


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance"
        )
