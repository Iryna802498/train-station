from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet
from .models import Station
from .serializers import StationSerializer
from .permissions import IsAdminOrIfAuthenticatedReadOnly


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
