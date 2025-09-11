from django.contrib import admin
from .models import (
    Station,
    TrainType,
    Crew,
    Route,
    Train,
    Journey,
    Order,
    Ticket
)


admin.site.register(Station)
admin.site.register(TrainType)
admin.site.register(Crew)
admin.site.register(Route)
admin.site.register(Train)
admin.site.register(Journey)
admin.site.register(Order)
admin.site.register(Ticket)
