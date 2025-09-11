from datetime import datetime
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import F, Count
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from .models import (
    Station,
    TrainType,
    Crew,
    Route,
    Train,
    Journey,
    Order
)
from .serializers import (
    StationSerializer,
    TrainTypeSerializer,
    TrainTypeImageSerializer,
    CrewSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    TrainSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    OrderSerializer,
    OrderListSerializer
)
from .permissions import IsAdminOrIfAuthenticatedReadOnly


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return TrainTypeImageSerializer
        return TrainTypeSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific train type"""
        train_type = self.get_object()
        serializer = self.get_serializer(train_type, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class TrainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        if self.action == "retrieve":
            return TrainDetailSerializer
        return TrainSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.select_related(
            "route",
            "train",
            "train__train_type")
        .prefetch_related("crew")
        .annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo")
                - Count("tickets", distinct=True)
            )
        )
    )
    serializer_class = JourneySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        source_name = self.request.query_params.get(
            "source_name"
        )
        destination_name = self.request.query_params.get(
            "destination_name"
        )
        train_name = self.request.query_params.get(
            "train_name"
        )
        departure_time = self.request.query_params.get(
            "departure_time"
        )
        arrival_time = self.request.query_params.get(
            "arrival_time"
        )
        queryset = self.queryset
        if source_name:
            queryset = queryset.filter(
                route__source__name__icontains=source_name
            )
        if destination_name:
            queryset = queryset.filter(
                route__destination__name__icontains=destination_name
            )
        if train_name:
            queryset = queryset.filter(
                train__name__icontains=train_name
            )
        if departure_time:
            departure_time = datetime.strptime(
                departure_time, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(
                departure_time__date=departure_time
            )
        if arrival_time:
            arrival_time = datetime.strptime(
                arrival_time, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(
                arrival_time__date=arrival_time
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer
        return JourneySerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source_name",
                type=OpenApiTypes.STR,
                description="Filter by source name (ex. ?source_name='Kiev')",
            ),
            OpenApiParameter(
                "destination_name",
                type=OpenApiTypes.STR,
                description="Filter by destination name (ex. ?destination_name='Kherson')",
            ),
            OpenApiParameter(
                "train_name",
                type=OpenApiTypes.STR,
                description="Filter by train name (ex. ?train_name='Intercity 723')",
            ),
            OpenApiParameter(
                "departure_time",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by departure time for Journey "
                    "(ex. ?departure_time=2025-09-23)"
                ),
            ),
            OpenApiParameter(
                "arrival_time",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by arrival time for Journey "
                    "(ex. ?arrival_time=2025-09-24)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = (Order.objects.select_related(
        "user",
        "tickets__journey__train",
        "tickets__journey__route__source",
        "tickets__journey__route__destination"
    )
    .prefetch_related("tickets__journey__crew")
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
