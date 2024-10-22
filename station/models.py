from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from django.core.exceptions import ValidationError

from station.utils import image_file_path


class Crew(models.Model):
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)

    @property
    def full_name(self):
        return str(self)

    class Meta:
        verbose_name_plural = "workers"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Station(models.Model):
    name = models.CharField(max_length=250)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "latitude", "longitude"],
                name="unique_station_constraint",
            )
        ]

    def __str__(self):
        return f"Station: {self.name}"


class TrainType(models.Model):
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return f"TrainType: {self.name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order, created_at: {self.created_at}, user: {self.user}"


class Train(models.Model):
    name = models.CharField(max_length=250)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType, on_delete=models.CASCADE, related_name="train_types"
    )
    image = models.ImageField(null=True, upload_to=image_file_path)

    @property
    def folder(self):
        return "uploads/train_images/"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "train_type"], name="unique_train_constraint"
            )
        ]

    def __str__(self):
        return f"Train: {self.name}"


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination", "distance"],
                name="unique_route_constraint",
            )
        ]

    def __str__(self):
        return f"Route, source: {self.source}, destination: {self.destination}"


class Journey(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    workers = models.ManyToManyField(Crew, related_name="trips")

    class Meta:
        ordering = ["departure_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["departure_time", "arrival_time", "route"],
                name="unique_journey_constraint",
            )
        ]

    def clean(self):
        super().clean()
        if self.departure_time < self.arrival_time:
            raise ValidationError(
                "Departure time must be greater than arrival time."
            )

    def __str__(self):
        return f"Journey, route: {self.route}, train: {self.train}"


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {train_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"Ticket, journey: {self.journey}, order: {self.order}"

    class Meta:
        unique_together = ["journey", "cargo", "seat"]
        ordering = ["cargo", "seat"]
