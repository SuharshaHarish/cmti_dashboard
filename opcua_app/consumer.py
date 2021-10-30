from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import SpindleSpeed,SpeedOverride,FeedOverride,FeedRate,CurrentPosition,MachineMode,MachineStatus,MachineDetails
from channels.db import database_sync_to_async

class DashConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.groupname='dashboard'
        await self.channel_layer.group_add(
            self.groupname,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self,close_code):

        await self.channel_layer.group_discard(
            self.groupname,
            self.channel_name
        )
    

    async def receive(self, text_data):
        datapoint = json.loads(text_data)
        # temperature = datapoint['temperature']
        # pressure  = datapoint['pressure']
        
        speedOvr = datapoint["speedOvr"]
        feedRateOvr = datapoint["feedRateOvr"]
        actSpeed = datapoint["actSpeed"] 
        mode = datapoint["mode"] 
        status = datapoint["status"]
        actPartProgram = datapoint["actPartProgram"]
        workPName = datapoint["workPName"] 
        progName = datapoint["progName"]
        fr_x = datapoint["fr_x"]  
        fr_y = datapoint["fr_y"] 
        fr_z = datapoint["fr_z"] 
        fr_b = datapoint["fr_b"] 
        cp_x = datapoint["cp_x"]
        cp_y = datapoint["cp_y"]
        cp_z = datapoint["cp_z"] 
        cp_b = datapoint["cp_b"]

        #save values to database
        await self.save_data(datapoint)

        await self.channel_layer.group_send(
            self.groupname,
            {
                'type':'deprocessing',
                # 'temperature': temperature,
                # 'pressure':pressure
                'speedOvr' : speedOvr,
                'feedRateOvr' : feedRateOvr,
                'actSpeed' : actSpeed,
                'mode' : mode,
                'status' : status,
                'actPartProgram' : actPartProgram,
                'workPName' : workPName,
                'progName' : progName,
                'fr_x' : fr_x,  
                'fr_y' : fr_y, 
                'fr_z' : fr_z, 
                'fr_b' : fr_b, 
                'cp_x' : cp_x,
                'cp_y' : cp_y,
                'cp_z' : cp_z, 
                'cp_b' : cp_b,
            }
        )
        # pass
        # print ('>>>>',text_data)

    async def deprocessing(self,event):
        # temperature = event['temperature']
        # pressure  = event['pressure']
        # await self.send(text_data=json.dumps({'temperature': temperature,'pressure':pressure}))
        speedOvr = event["speedOvr"]
        feedRateOvr = event["feedRateOvr"]
        actSpeed = event["actSpeed"] 
        mode = event["mode"] 
        status = event["status"]
        actPartProgram = event["actPartProgram"]
        workPName = event["workPName"] 
        progName = event["progName"]
        fr_x = event["fr_x"]  
        fr_y = event["fr_y"] 
        fr_z = event["fr_z"] 
        fr_b = event["fr_b"] 
        cp_x = event["cp_x"]
        cp_y = event["cp_y"]
        cp_z = event["cp_z"] 
        cp_b = event["cp_b"]

        await self.send(text_data=json.dumps({
            'speedOvr' : speedOvr,
            'feedRateOvr' : feedRateOvr,
            'actSpeed' : actSpeed,
            'mode' : mode,
            'status' : status,
            'actPartProgram' : actPartProgram,
            'workPName' : workPName,
            'progName' : progName,
            'fr_x' : fr_x,  
            'fr_y' : fr_y, 
            'fr_z' : fr_z, 
            'fr_b' : fr_b, 
            'cp_x' : cp_x,
            'cp_y' : cp_y,
            'cp_z' : cp_z, 
            'cp_b' : cp_b,
            }))

    @database_sync_to_async
    def save_data(self, data):
        #save values to database

        # temperature = data['temperature']
        # pressure  = data['pressure']
        # temp = Temperature.objects.create(temp_value = temperature)
        # temp.save()

        # pres = Pressure.objects.create(pres_value = pressure)
        # pres.save()

        speedOvr = data["speedOvr"]     
        speedOvr_obj = SpeedOverride.objects.create(speed_override_value = speedOvr)
        speedOvr_obj.save()

        feedRateOvr = data["feedRateOvr"]
        feedRateOvr_obj = FeedOverride.objects.create(feed_override_value = feedRateOvr)
        feedRateOvr_obj.save()  

        actSpeed = data["actSpeed"]    
        actSpeed_obj = SpindleSpeed.objects.create(spindle_speed_value = actSpeed)
        actSpeed_obj.save()   

        mode = data["mode"]  
        prev_mode = MachineMode.objects.last()
        if prev_mode.mode_value != mode: 
            mode_obj = MachineMode.objects.create(mode_value = mode)
            mode_obj.save()   

        status = data["status"]
        prev_status = MachineStatus.objects.last()
        if prev_status.status_value != status:
            status_obj = MachineStatus.objects.create(status_value = status)
            status_obj.save()   

        actPartProgram = data["actPartProgram"]
        workPName = data["workPName"] 
        progName = data["progName"]
        prev_details = MachineDetails.objects.last()
        if prev_details.actPartProgram == actPartProgram and prev_details.workPName == workPName and prev_details.progName == progName:
            pass
        else: 
            details_obj = MachineDetails.objects.create(actPartProgram = actPartProgram, workPName=workPName, progName=progName)
            details_obj.save()

        fr_x = data["fr_x"]  
        fr_y = data["fr_y"] 
        fr_z = data["fr_z"] 
        fr_b = data["fr_b"]
        feedRate_obj = FeedRate.objects.create(x_axis = fr_x , y_axis = fr_y , z_axis = fr_z , b_axis = fr_b )
        feedRate_obj.save()  

        cp_x = data["cp_x"]
        cp_y = data["cp_y"]
        cp_z = data["cp_z"] 
        cp_b = data["cp_b"]
        currentPosition_obj = CurrentPosition.objects.create(x_axis = cp_x , y_axis = cp_y , z_axis = cp_z , b_axis = cp_b )
        currentPosition_obj.save()    