from django.db import models
from django.db.models.deletion import CASCADE
from django.utils import timezone 
from django.db import connection

# class Temperature(models.Model):

#     temp_value = models.IntegerField(default=0)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return str(self.temp_value)

# class Pressure(models.Model):

#     pres_value = models.IntegerField(default=0)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return str(self.pres_value)

class SpeedOverride(models.Model):

    speed_override_value = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.speed_override_value)

class SpindleSpeed(models.Model):

    spindle_speed_value = models. FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.spindle_speed_value)
                
class FeedOverride(models.Model):

    feed_override_value = models. FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.feed_override_value)
                
class FeedRate(models.Model):

    x_axis = models. FloatField(default=0)
    y_axis = models. FloatField(default=0)
    z_axis = models. FloatField(default=0)
    b_axis = models. FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return str(self.feed_override_value)
                
class CurrentPosition(models.Model):

    x_axis = models. FloatField(default=0)
    y_axis = models. FloatField(default=0)
    z_axis = models. FloatField(default=0)
    b_axis = models. FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return str(self.feed_override_value)

class MachineMode(models.Model):

    class ModeChoices(models.IntegerChoices):
        JOG = 0
        MDI = 1
        AUTO = 2

    mode_value = models.IntegerField(choices=ModeChoices.choices)     
    timestamp = models.DateTimeField(auto_now_add=True)

class MachineStatus(models.Model):

    class StatusChoices(models.IntegerChoices):
        ABORTED = 0
        HALTED = 1
        RUNNING = 2
        WAITING = 3
        INTERRUPTED = 4

    status_value = models.IntegerField(choices=StatusChoices.choices)     
    timestamp = models.DateTimeField(auto_now_add=True)

class MachineDetails(models.Model):

    actPartProgram = models.CharField(default="",max_length=250)
    workPName = models.CharField(default="",max_length=250)
    progName = models.CharField(default="",max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)


class Anomaly(models.Model):

    PARAM_CHOICES = (
        ('s','speedOvr'),
        ('f','feedRateOvr'),
        ('a','actSpeed')
    )
    param_type = models.CharField(choices=PARAM_CHOICES,null=False,max_length=20)
    speedOvr_key = models.ForeignKey(SpeedOverride,on_delete=CASCADE,null=True)
    feedRateOvr_key = models.ForeignKey(FeedOverride,on_delete=CASCADE,null=True)
    actSpeed_key = models.ForeignKey(SpindleSpeed,on_delete=CASCADE,null=True)

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {} CASCADE'.format(cls._meta.db_table))

    def __str__(self):

        if self.param_type == 's':
            return ("Speed Override "+str(self.speedOvr_key.timestamp))
        elif self.param_type == 'f':
            return ("Feed Override "+str(self.feedRateOvr_key.timestamp))
        else:
            return ("Spindle Speed "+str(self.actSpeed_key.timestamp))

