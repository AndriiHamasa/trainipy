from rest_framework import serializers

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


class JourneySerializer(serializers.ModelSerializer):
    departure_place = serializers.CharField(source="route.source.name")
    arrival_place = serializers.CharField(source="route.destination.name")
    train = TrainJourneySerializer()

    class Meta:
        model = Journey
        fields = ("id", "departure_place", "arrival_place", "train", "departure_time", "arrival_time", "count_workers")
