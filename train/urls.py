from django.urls import path, include
from rest_framework import routers
from .views import StationViewSet, TrainTypeViewSet


router = routers.DefaultRouter()
router.register("stations", StationViewSet, basename="station")
router.register("train-types", TrainTypeViewSet, basename="train-type")
urlpatterns = [
    path("", include(router.urls)),
]


app_name = "train"
