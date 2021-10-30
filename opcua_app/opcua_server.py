"""
This is the opc ua demo server python script.
Running this script will start a demo opc ua server with default parameters i.e. temperature & pressure.
You can edit the code to add more parameters as per your requirement
NOTE: Change the URL with the IP address of your system. If 4840 port is blocked, you can use any other port
"""

from opcua import Server
from random import randint,choice
import time
import sys

server = Server()
url = "opc.tcp://192.168.0.246:4840"
server.set_endpoint(url)
name = "Rocket_Systems_OPCUA_Simulation_Server"
add_space = server.register_namespace(name)

node = server.get_objects_node()
param = node.add_object(add_space, "Parameters")

temp = param.add_variable(add_space, "Temperature", 0)
press = param.add_variable(add_space, "Pressure", 0)
temp.set_writable()
press.set_writable()

server.start()
print("Server started at {}".format(url))

try:
    while True:
        anomaly_factor = randint(0,10)
        if anomaly_factor > 7:
            #generate anomaly values
            temp_range = list(range(0,10)) + list(range(31,50))
            temperature = choice(temp_range)
            pres_range = list(range(0,500)) + list(range(2201,3000))
            pressure = choice(pres_range)            
        else:
            #generate normal values
            temperature = randint(10, 31)
            pressure = randint(500,2201)
            
        print(pressure, temperature)

        temp.set_value(temperature)
        press.set_value(pressure)

        time.sleep(2)

except KeyboardInterrupt:
    server.stop()
    print("Server closed")
    sys.exit()

