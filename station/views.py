from drf_spectacular.types import OpenApiTypes
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import GenericViewSet
from django.db.models import Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from station.models import (
    Crew,
    Train,
    TrainType,
    Station,
    Route,
    Journey,
    Order
)
from station.serializers import (
    CrewSerializer,
    TrainSerializer,
    TrainCreateSerializer,
    TrainTypeSerializer,
    StationSerializer,
    RouteSerializer,
    JourneyListSerializer,
    JourneyCreateSerializer,
    JourneyDetailSerializer,
    RouteCreateSerializer,
    OrderListSerializer,
    OrderSerializer,
    TrainImageSerializer,
)
from station.utils import params_to_ints


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_queryset(self):
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        queryset = super().get_queryset()

        if first_name and last_name:
            return queryset.filter(
                first_name__icontains=first_name,
                last_name__icontains=last_name
            )
        elif first_name:
            return queryset.filter(first_name__icontains=first_name)
        elif last_name:
            return queryset.filter(last_name__icontains=last_name)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "first_name",
                type=OpenApiTypes.STR,
                description="Filter by first_name id (ex. ?first_name=Jo)",
            ),
            OpenApiParameter(
                "last_name",
                type=OpenApiTypes.STR,
                description="Filter by last_name id (ex. ?last_name=Gre)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of movies"""
        return super().list(request, *args, **kwargs)


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Train.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset().select_related("train_type")

        if self.action == "list":
            name = self.request.query_params.get("name")
            if name:
                return queryset.filter(name__icontains=name)

            return queryset

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TrainSerializer
        if self.action == "retrieve":
            return TrainCreateSerializer
        if self.action == "create":
            return TrainCreateSerializer
        if self.action == "upload_image":
            return TrainImageSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific train"""
        train = self.get_object()
        serializer = self.get_serializer(train, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by name id (ex. ?name=qui)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of movies"""
        return super().list(request, *args, **kwargs)


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        name = self.request.query_params.get("name")
        latitude = self.request.query_params.get("latitude")
        longitude = self.request.query_params.get("longitude")

        if name:
            queryset = queryset.filter(name__icontains=name)
        if latitude:
            queryset = queryset.filter(latitude=float(latitude))
        if longitude:
            queryset = queryset.filter(longitude=float(longitude))

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by name id (ex. ?name=Lvi)",
            ),
            OpenApiParameter(
                "latitude",
                type=OpenApiTypes.FLOAT,
                description="Filter by latitude id (ex. ?latitude=49.9808)",
            ),
            OpenApiParameter(
                "longitude",
                type=OpenApiTypes.FLOAT,
                description="Filter by longitude id (ex. ?longitude=36.176)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of movies"""
        return super().list(request, *args, **kwargs)


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.select_related("source", "destination")

    def get_queryset(self):
        queryset = super().get_queryset()

        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if source:
            source_ids = params_to_ints(source)
            queryset = queryset.filter(source_id__in=source_ids)
        if destination:
            destination_ids = params_to_ints(destination)
            queryset = queryset.filter(destination_id__in=destination_ids)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteSerializer
        if self.action == "create":
            return RouteCreateSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source id (ex. ?source=1,2)",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by destination id (ex. ?destination=2,3)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of movies"""
        return super().list(request, *args, **kwargs)


class JourneyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Journey.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == "list":
            queryset = queryset.select_related(
                "route__source",
                "route__destination",
                "train",
                "train__train_type"
            ).annotate(count_workers=Count("workers"))

            route = self.request.query_params.get("route")
            train = self.request.query_params.get("train")

            if route:
                route_ids = params_to_ints(route)
                queryset = queryset.filter(route_id__in=route_ids)
            if train:
                train_ids = params_to_ints(train)
                queryset = queryset.filter(route_id__in=train_ids)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "create":
            return JourneyCreateSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "route",
                type=OpenApiTypes.STR,
                description="Filter by route id (ex. ?route=1,2)",
            ),
            OpenApiParameter(
                "train",
                type=OpenApiTypes.STR,
                description="Filter by train id (ex. ?train=2,3)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of movies"""
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .prefetch_related("tickets")
        )

        date = self.request.query_params.get("date")
        journey = self.request.query_params.get("journey")

        if date:
            queryset = queryset.filter(created_at__date=date)
        if journey:
            journey_ids = params_to_ints(journey)
            queryset = queryset.filter(tickets__journey__id__in=journey_ids)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "date",
                type=OpenApiTypes.DATE,
                description="Filter by date id (ex. ?date=2024-10-13)",
            ),
            OpenApiParameter(
                "journey",
                type=OpenApiTypes.STR,
                description="Filter by journey id (ex. ?journey=2,3)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of movies"""
        return super().list(request, *args, **kwargs)
