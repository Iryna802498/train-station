from django.urls import path, include
from rest_framework import routers
from .views import StationViewSet


router = routers.DefaultRouter()
router.register("stations", StationViewSet, basename="station")
urlpattern = [
    path("", include(router.urls)),
]


app_name = "train"
