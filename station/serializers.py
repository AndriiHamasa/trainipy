from django.utils import timezone

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from station.models import Crew, Train, TrainType, Station, Route, Journey


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    train_type = serializers.CharField(source="train_type.name")

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainCreateSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        many=False,
        queryset=TrainType.objects.all(),
        slug_field="name"
    )


class TrainJourneySerializer(TrainSerializer):
    class Meta:
        model = Train
        fields = ("name", "train_type")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source="source.name")
    destination = serializers.CharField(source="destination.name")

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteCreateSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        many=False,
        queryset=Station.objects.all(),
        slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        many=False,
        queryset=Station.objects.all(),
        slug_field="name"
    )


class JourneyListSerializer(serializers.ModelSerializer):
    departure_place = serializers.CharField(source="route.source.name")
    arrival_place = serializers.CharField(source="route.destination.name")
    train = TrainJourneySerializer()
    count_workers = serializers.IntegerField()

    class Meta:
        model = Journey
        fields = (
            "id",
            "departure_place",
            "arrival_place",
            "train",
            "departure_time",
            "arrival_time",
            "count_workers",
        )


class JourneyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "workers")

    def validate_departure_time(self, value):
        if value < timezone.now():
            raise ValidationError("Departure time cannot be in the past.")
        return value

    def validate_arrival_time(self, value):
        if value < timezone.now():
            raise ValidationError("Arrival time cannot be in the past.")
        return value

    def validate(self, attrs):
        departure_time = attrs.get("departure_time")
        arrival_time = attrs.get("arrival_time")

        if departure_time >= arrival_time:
            raise ValidationError("Departure time must be earlier than arrival time.")

        # Проверка на уникальность Journey
        route = attrs.get("route")
        if Journey.objects.filter(departure_time=departure_time, arrival_time=arrival_time, route=route).exists():
            raise ValidationError("Journey with this departure, arrival time and route already exists.")

        return attrs


class JourneyDetailSerializer(JourneyCreateSerializer):
    route = RouteSerializer()
    train = TrainSerializer()
    workers = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )

    # class Meta:
    #     model = Journey
    #     fields = ("id", "route", "train", "departure_time", "arrival_time", "workers")

