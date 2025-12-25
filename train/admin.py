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


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInLine,)


admin.site.register(Station)
admin.site.register(TrainType)
admin.site.register(Crew)
admin.site.register(Route)
admin.site.register(Train)
admin.site.register(Journey)
admin.site.register(Ticket)
