import RPi.GPIO as GPIO 
import time
from i2c_sniffer import I2CSniffer
import RPi.GPIO as GPIO

SDA = 2
SCL = 3
GPIO_TRIGGER = 4

class Pyrometer:
    def __init__(self):
        self.i2c_sniffer = I2CSniffer(SDA, SCL, self._cb)
        self.gpio_trigger = GPIO_TRIGGER

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_trigger, GPIO.OUT)

        self.frames = list()

    def _cb(self, frame):
        self.frames.append(frame)

    def measure(self):
        self.frames = list()
        self.i2c_sniffer.sniff()
        GPIO.output(self.gpio_trigger, True)
        print("Medir*")
        time.sleep(3)
        GPIO.output(self.gpio_trigger, False)
        time.sleep(1)
        self.i2c_sniffer.stop()

        if len(self.frames) == 3:
            self.decode_temperature(self.frames[2])

    def decode_temperature(self, frame):
        frame = filter(lambda x: x != '[' and x != ']', frame)
        if len(frame) > 0 and frame[len(frame)-1] == '+':
            frame = frame[:-1]

        byte_fields = frame.split('+')

        if len(byte_fields) != 4:
            return

        temp_str = "0x" + byte_fields[3][1] + byte_fields[2]
        temp = int(temp_str, 16) 
        temp_float = temp / 100.0
        print("temperature: " + str(temp_float))
        

        
        
        

