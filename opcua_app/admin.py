from django.contrib import admin
from .models import SpindleSpeed,SpeedOverride,FeedOverride,FeedRate,CurrentPosition,MachineMode,MachineStatus,MachineDetails, Anomaly

# admin.site.register(Temperature)
# admin.site.register(Pressure)
admin.site.register(Anomaly)
admin.site.register(SpindleSpeed)
admin.site.register(SpeedOverride)
admin.site.register(FeedOverride)
admin.site.register(FeedRate)
admin.site.register(CurrentPosition)
admin.site.register(MachineMode)
admin.site.register(MachineStatus)
admin.site.register(MachineDetails)

