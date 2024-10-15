from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from station.models import TrainType
from station.serializers import TrainTypeSerializer
from rest_framework import status


TRAIN_TYPE_URL = reverse("station:traintype-list")

def sample_train_type(**params):
    defaults = {
        "name": "default_train_type",
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)


class UnauthenticatedAndAuthenticatedTrainTypeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.train_type = sample_train_type()

    def test_station_list(self):
        res = self.client.get(TRAIN_TYPE_URL)
        train_type_list = TrainType.objects.all()
        serializer = TrainTypeSerializer(train_type_list, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)


class AuthenticatedTrainTypeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="test1234"
        )
        self.client.force_authenticate(self.user)
        self.station= sample_train_type()

    def test_create_crew_forbidden(self):
        payload = {
            "name": "test",
        }

        res = self.client.post(TRAIN_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainTypeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@test.com", password="test1234"
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        payload = {
            "name": "test",
        }

        res = self.client.post(TRAIN_TYPE_URL, payload)

        movie = TrainType.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(movie, key))
