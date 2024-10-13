from rest_framework import routers
from django.urls import path, include
from station.views import CrewViewSet, TrainViewSet, TrainTypeViewSet, StationViewSet, RouteViewSet, JourneyViewSet

router = routers.DefaultRouter()
router.register("crew", CrewViewSet)
router.register("trains", TrainViewSet)
router.register("train-types", TrainTypeViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("journeys", JourneyViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "station"