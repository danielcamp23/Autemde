import time
import string  
import json 
import datetime

#from src.ramp import Ramp 
#from src.servo import Servo
#from src.id_detector import IDDetector
from src.pyrometer import Pyrometer
#from src.id_detector import IDDetector
from src.id_scanner import IDScanner
from src.mqtt_client import MQTTClient


def id_card_detected(msg):
    print(msg)
    fields = msg.split(',')
    global id_fields
    id_fields = list()

    for field in fields:
        filtered = filter(lambda x: x in string.printable, field)
        str_ = ""
        f = str_.join(filtered)
        id_fields.append(f.strip())

    print("card detected")
    global is_card_detected
    is_card_detected = True

def temperature_taken(temp):
    global temperature
    temperature = temp

    print("temp taken")
    global is_temperature_taken
    is_temperature_taken = True

def publish_msg():
    x = {
        "name": id_fields[5] + " " + id_fields[6],
        "lastName" : id_fields[3] + " " + id_fields[4],
        "id" : id_fields[2],
        "birthday" : id_fields[8],
        "temperature": temperature,
        "company" : "62b15004-a85d-11ea-bb37-0242ac130002",
        "device" : "dbafb884-a85c-11ea-bb37-0242ac130002",
        "timestamp" : int(datetime.datetime.now().timestamp()) * 1000
    }

    print(json.dumps(x))
    mqtt_client.publish_msg(json.dumps(x))

mqtt_client = MQTTClient()
id_scanner = IDScanner(id_card_detected)
pyrometer = Pyrometer(temperature_taken)

is_card_detected = False
is_temperature_taken = False
id_fields = list()
temperature = ""

if __name__ == "__main__":

    id_scanner.start()
    while True:
        if is_card_detected and not is_temperature_taken:
            pyrometer.measure()
        elif is_card_detected and is_temperature_taken:
            publish_msg()
            is_card_detected = False
            is_temperature_taken = False
        time.sleep(1.5)

    print("Main thread finished!")







