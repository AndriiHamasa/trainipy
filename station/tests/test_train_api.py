from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from station.models import Train, TrainType
from station.serializers import TrainSerializer
from rest_framework import status


TRAIN_URL = reverse("station:train-list")


def sample_train_type(name):
    defaults = {"name": name}

    return TrainType.objects.create(**defaults)


def sample_train(train_type, **params):
    defaults = {
        "name": "test_train",
        "cargo_num": 1,
        "places_in_cargo": 56,
        "train_type": train_type,
    }
    defaults.update(params)

    return Train.objects.create(**defaults)


class UnauthenticatedAndAuthenticatedTrainAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.train = sample_train(
            train_type=sample_train_type(name="default_train_type")
        )

    def test_train_list(self):
        res = self.client.get(TRAIN_URL)
        station_list = Train.objects.all()
        serializer = TrainSerializer(station_list, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_train(self):
        second_train = sample_train(
            name="test_train_3", train_type=sample_train_type(name="quick")
        )

        res = self.client.get(TRAIN_URL, {"name": self.train.name})

        serializer_first = TrainSerializer(self.train)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_first.data, res.data["results"])


class AuthenticatedTrainAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="test1234"
        )
        self.client.force_authenticate(self.user)

    def test_create_train_forbidden(self):
        payload = {
            "name": "test_train",
            "cargo_num": 1,
            "places_in_cargo": 56,
            "train_type": sample_train_type(name="default_train_type"),
        }

        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@test.com", password="test1234"
        )
        self.client.force_authenticate(self.user)
