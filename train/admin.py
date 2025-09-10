from django.contrib import admin
from .models import Station, TrainType, Crew, Route


admin.site.register(Station)
admin.site.register(TrainType)
admin.site.register(Crew)
admin.site.register(Route)
