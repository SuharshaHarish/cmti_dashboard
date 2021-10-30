from opcua import Client
import time,json,sys
import websocket,socket
import requests
from datetime import datetime,timedelta

url = "opc.tcp://14.139.152.103:4840"
# url = "opc.tcp://192.168.0.246:4840"
client = Client(url)

def handle_error(e):

    # current_time = datetime(year=2021,month=10,day=30,hour=16,minute=59,second=45)
    current_time = datetime.now()

    #Check if its weekend
    if current_time.weekday() >= 5:
        if current_time.weekday() == 5:
            next_day = datetime(year=current_time.year,month=current_time.month,day=current_time.day) + timedelta(days=2)
            start = datetime(year=next_day.year,month=next_day.month,day=next_day.day,hour=9)
            waiting_time = start-current_time
            print("Retrying Connection in {0} seconds".format(waiting_time.total_seconds()))
            time.sleep(waiting_time.total_seconds())
            print("Trying to connect...")
        
        if current_time.weekday() == 6:
            next_day = datetime(year=current_time.year,month=current_time.month,day=current_time.day) + timedelta(days=1)
            start = datetime(year=next_day.year,month=next_day.month,day=next_day.day,hour=9)
            waiting_time = start-current_time
            print("Retrying Connection in {0} seconds".format(waiting_time.total_seconds()))
            time.sleep(waiting_time.total_seconds())
            print("Trying to connect...")

    #Check if its after office hrs(9am-5pm)
    else:
        if current_time.hour < 9:
            start = datetime(year=current_time.year,month=current_time.month,day=current_time.day,hour=9)
            waiting_time = start-current_time
            print("Retrying Connection in {0} seconds".format(waiting_time.total_seconds()))
            time.sleep(waiting_time.total_seconds())
            print("Trying to connect...")

        elif current_time.hour >= 17:
            next_day = datetime(year=current_time.year,month=current_time.month,day=current_time.day) + timedelta(days=1)
            start = datetime(year=next_day.year,month=next_day.month,day=next_day.day,hour=9)
            waiting_time = start-current_time
            print("Retrying Connection in {0} seconds".format(waiting_time.total_seconds()))
            time.sleep(waiting_time.total_seconds())
            print("Trying to connect...")
            
        else:       
            print("Retrying Connection in 10 seconds") 
            print("Trying to connect...")
            time.sleep(10)

def connection_loop():

    client.set_user("OpcUaClient")
    client.set_password("OpcUaClient")
    client.connect()
    data = dict()

    ws = websocket.WebSocket()
    ws.connect('ws://localhost:8000/ws/polData')

    while True:
        try:
            speedOvr = client.get_node("ns=2;s=/Channel/Spindle/speedOvr").get_value()
            feedRateOvr = client.get_node("ns=2;s=/Channel/MachineAxis/feedRateOvr").get_value()
            actSpeed = client.get_node("ns=2;s=/Channel/Spindle/actSpeed").get_value()

            mode = client.get_node("ns=2;s=/Bag/State/opMode").get_value()
            status = client.get_node("ns=2;s=/Channel/State/acProg").get_value()

            actPartProgram = client.get_node("ns=2;s=/Channel/ProgramInfo/actPartProgram").get_value()
            workPName = client.get_node("ns=2;s=/Channel/ProgramInfo/workPName").get_value()
            progName = client.get_node("ns=2;s=/Channel/ProgramInfo/progName").get_value()

            fr_x = client.get_node("ns=2;s=/Channel/MachineAxis/actFeedRate[u1,1]").get_value()
            fr_y = client.get_node("ns=2;s=/Channel/MachineAxis/actFeedRate[u1,2]").get_value()
            fr_z = client.get_node("ns=2;s=/Channel/MachineAxis/actFeedRate[u1,3]").get_value()
            fr_b = client.get_node("ns=2;s=/Channel/MachineAxis/actFeedRate[u1,4]").get_value()
            
            cp_x = client.get_node("ns=2;s=/Nck/MachineAxis/aaDtbb[u1,1]").get_value()
            cp_y = client.get_node("ns=2;s=/Nck/MachineAxis/aaDtbb[u1,2]").get_value()
            cp_z = client.get_node("ns=2;s=/Nck/MachineAxis/aaDtbb[u1,3]").get_value()
            cp_b = client.get_node("ns=2;s=/Nck/MachineAxis/aaDtbb[u1,4]").get_value()

            # temp = client.get_node("ns=2;i=2")
            # press = client.get_node("ns=2;i=3")
            # temperature = temp.get_value()
            # pressure = press.get_value()
            # print(pressure, temperature)
            # data["temperature"] = int(temperature)
            # data["pressure"] = int(pressure)

            data["speedOvr"] = speedOvr
            data["feedRateOvr"] = feedRateOvr
            data["actSpeed"] = actSpeed
            data["mode"] = mode
            data["status"] = status
            data["actPartProgram"] = actPartProgram
            data["workPName"] = workPName
            data["progName"] = progName
            data["fr_x"] = fr_x
            data["fr_y"] = fr_y
            data["fr_z"] = fr_z
            data["fr_b"] = fr_b
            data["cp_x"] = cp_x
            data["cp_y"] = cp_y
            data["cp_z"] = cp_z
            data["cp_b"] = cp_b
            print(data)
            ws.send(json.dumps(data))
            time.sleep(2)
        except Exception as e:            
            print("Caught timeout",e.__class__.__name__)
            handle_error(e)
            break


while True:    
    try:
        connection_loop()

    except (KeyboardInterrupt):
        client.disconnect()
        print("Client closed")
        sys.exit()

    except(ConnectionResetError):
        client.disconnect()
        print("Client closed test")
        sys.exit()

    # except(ConnectionRefusedError):
    #     # client.disconnect()
    #     print("Connection Refused by dashboard Client closed")
    #     sys.exit()

    except Exception as e:

        # print("Error: ", e)
        # print("Connection Refused by dashboard Client closed")            
        # sys.exit()
        print("Server unavailable")    
        handle_error(e)