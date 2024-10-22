from django.contrib import admin

from station.models import (
    Crew,
    Station,
    TrainType,
    Order,
    Train,
    Route,
    Journey,
    Ticket,
)

admin.site.register(Crew)
admin.site.register(Station)
admin.site.register(TrainType)
admin.site.register(Order)
admin.site.register(Train)
admin.site.register(Route)
admin.site.register(Journey)
admin.site.register(Ticket)
