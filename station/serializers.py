from django.db import transaction
from django.utils import timezone

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from station.models import (
    Crew,
    Train,
    TrainType,
    Station,
    Route,
    Journey,
    Ticket,
    Order,
)


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
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "image"
        )


class JourneyTrainSerializer(serializers.ModelSerializer):
    departure_place = serializers.CharField(source="route.source.name")
    arrival_place = serializers.CharField(source="route.destination.name")

    class Meta:
        model = Journey
        fields = (
            "id",
            "departure_place",
            "arrival_place",
            "departure_time",
            "arrival_time",
        )


class TrainCreateSerializer(serializers.ModelSerializer):
    journeys = serializers.SerializerMethodField()

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "journeys",
        )

    def get_journeys(self, obj):
        last_five_journeys = obj.journeys.select_related(
            "route__source", "route__destination"
        ).order_by("-id")[:5]
        return JourneyTrainSerializer(last_five_journeys, many=True).data


class TrainImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "image")


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
        many=False, queryset=Station.objects.all(), slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        many=False, queryset=Station.objects.all(), slug_field="name"
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
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "workers"
        )

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
            raise ValidationError(
                "Departure time must be earlier than arrival time."
            )

        route = attrs.get("route")
        if Journey.objects.filter(
            departure_time=departure_time,
            arrival_time=arrival_time,
            route=route
        ).exists():
            raise ValidationError(
                "Journey with this departure, arrival time "
                "and route already exists."
            )

        return attrs


class JourneyDetailSerializer(JourneyCreateSerializer):
    route = RouteSerializer()
    train = TrainSerializer()
    workers = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["journey"].train,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")  # "order"


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")
        write_only_fields = ("tickets",)

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)

            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)

            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
