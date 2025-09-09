from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet
from .models import Station, TrainType
from .serializers import StationSerializer, TrainTypeSerializers
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
    GenericViewSet
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializers
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)