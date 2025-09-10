from rest_framework import serializers
from .models import (
    Station,
    TrainType,
    Crew,
    Route,
    Train,
    Journey
)


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


class TrainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type"
        )


class TrainListSerializer(TrainSerializer):
    train_type_name = serializers.CharField(
        source="train_type.name",
        read_only=True
    )
    train_type_image = serializers.ImageField(
        source="train_type.image",
        read_only=True
    )

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type_name",
            "train_type_image",
            "total_places"
        )


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(read_only=True)

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type"
        )


class JourneySerializer(serializers.ModelSerializer):

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "crew",
            "departure_time",
            "arrival_time"
        )


class JourneyListSerializer(JourneySerializer):
    train_name = serializers.CharField(
        source="train.name",
        read_only=True
    )
    train_type_name = serializers.CharField(
        source="train.train_type.name",
        read_only=True
    )
    route_source = serializers.CharField(
        source="route.source.name",
        read_only=True
    )
    route_destination = serializers.CharField(
        source="route.destination.name",
        read_only=True
    )
    crew = serializers.SerializerMethodField(read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "route_source",
            "route_destination",
            "train_name",
            "train_type_name",
            "crew",
            "departure_time",
            "arrival_time",
            "tickets_available"
        )

    def get_crew(self, obj):
        return [
            {
                "full_name": crew.full_name,
                "position": crew.position
            }
            for crew in obj.crew.all()
        ]


class JourneyDetailSerializer(JourneySerializer):
    route = RouteSerializer(read_only=True)
    train = TrainSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "crew",
            "departure_time",
            "arrival_time"
        )
