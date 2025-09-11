from django.urls import path, include
from rest_framework import routers
from .views import (
    StationViewSet,
    TrainTypeViewSet,
    CrewViewSet,
    RouteViewSet,
    TrainViewSet,
    JourneyViewSet,
    OrderViewSet
    )


router = routers.DefaultRouter()
router.register("stations", StationViewSet, basename="station")
router.register("train-types", TrainTypeViewSet, basename="train-type")
router.register("crews", CrewViewSet, basename="crew")
router.register("routers", RouteViewSet, basename="route")
router.register("trains", TrainViewSet, basename="train")
router.register("journeys", JourneyViewSet, basename="journey")
router.register("orders", OrderViewSet, basename="order")
urlpatterns = [
    path("", include(router.urls)),
]


app_name = "train"
