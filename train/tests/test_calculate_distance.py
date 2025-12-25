import pytest
from math import isclose

from train.models import Station, Route, calculate_distance

@pytest.mark.django_db
def test_calculate_distance_function():
    kyiv_lat, kyiv_lon = 50.45466, 30.5238
    lviv_lat, lviv_lon = 49.84295, 24.0311
    distance = calculate_distance(kyiv_lat, kyiv_lon, lviv_lat, lviv_lon)
    assert isclose(distance, 471, rel_tol=0.05)


@pytest.mark.django_db
def test_route_distance_is_set_automatically():
    kyiv = Station.objects.create(
        name="Kyiv",
        latitude=50.45466,
        longitude=30.5238
    )
    lviv = Station.objects.create(
        name="Lviv",
        latitude=49.84295,
        longitude=24.0311
    )

    route = Route.objects.create(source=kyiv, destination=lviv)

    assert route.distance > 0
    assert isclose(route.distance, 471, rel_tol=0.05)
