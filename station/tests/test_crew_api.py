from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from station.models import Crew
from station.serializers import CrewSerializer
from rest_framework import status


CREW_URL = reverse("station:crew-list")


def sample_crew(**params):
    defaults = {
        "first_name": "Peter",
        "last_name": "Parker",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


class UnauthenticatedAndAuthenticatedCrewAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.crew = sample_crew()

    def test_crew_list(self):
        res = self.client.get(CREW_URL)
        crew_list = Crew.objects.all()
        serializer = CrewSerializer(crew_list, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_crew(self):
        zoe_crew = sample_crew(first_name="Zoe", last_name="Zoe")
        fred_crew = sample_crew(first_name="Fred", last_name="Fred")
        default_crew = sample_crew(first_name="John", last_name="Doe")

        for filter_field, filter_value in [
            ("first_name", default_crew.first_name),
            ("last_name", default_crew.last_name),
        ]:
            res = self.client.get(CREW_URL, {filter_field: filter_value})

            serializer_default = CrewSerializer(default_crew)
            serializer_zoe_crew = CrewSerializer(zoe_crew)
            serializer_fred_crew = CrewSerializer(fred_crew)

            assert res.status_code == status.HTTP_200_OK
            assert serializer_default.data in res.data["results"]
            assert serializer_zoe_crew.data not in res.data["results"]
            assert serializer_fred_crew.data not in res.data["results"]


class AuthenticatedCrewAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="test1234"
        )
        self.client.force_authenticate(self.user)
        self.crew = sample_crew()

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "test",
            "last_name": "test",
        }

        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@test.com", password="test1234"
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        payload = {
            "first_name": "test",
            "last_name": "test",
        }

        res = self.client.post(CREW_URL, payload)

        movie = Crew.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(movie, key))
