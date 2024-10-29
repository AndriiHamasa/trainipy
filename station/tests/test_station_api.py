from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from station.models import Station
from station.serializers import StationSerializer
from rest_framework import status


STATION_URL = reverse("station:station-list")


def sample_station(**params):
    defaults = {
        "name": "test_station",
        "latitude": 45.5689,
        "longitude": 45.5689
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


class UnauthenticatedAndAuthenticatedStationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.station = sample_station()

    def test_station_list(self):
        res = self.client.get(STATION_URL)
        station_list = Station.objects.all()
        serializer = StationSerializer(station_list, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_station(self):
        first_station = sample_station(
            name="test2", latitude=43.5679, longitude=43.5679
        )
        second_station = sample_station(
            name="test3", latitude=45.5679, longitude=45.5679
        )
        third_station = sample_station(
            name="test4", latitude=45.6679, longitude=45.6679
        )

        for filter_field, filter_value in [
            ("name", first_station.name),
            ("latitude", first_station.latitude),
            ("longitude", first_station.longitude),
        ]:
            res = self.client.get(STATION_URL, {filter_field: filter_value})

            serializer_first = StationSerializer(first_station)
            serializer_second = StationSerializer(second_station)
            serializer_third = StationSerializer(third_station)

            assert res.status_code == status.HTTP_200_OK
            assert serializer_first.data in res.data["results"]
            assert serializer_second.data not in res.data["results"]
            assert serializer_third.data not in res.data["results"]


class AuthenticatedStationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="test1234"
        )
        self.client.force_authenticate(self.user)
        self.station = sample_station()

    def test_create_crew_forbidden(self):
        payload = {
            "name": "test0",
            "latitude": 11.1111,
            "longitude": 22.2222,
        }

        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminMovieTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@test.com", password="test1234"
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        payload = {
            "name": "test0",
            "latitude": 11.1111,
            "longitude": 22.2222,
        }

        res = self.client.post(STATION_URL, payload)

        movie = Station.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(movie, key))
