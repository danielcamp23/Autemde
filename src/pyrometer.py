import RPi.GPIO as GPIO 
import time
from i2c_sniffer import I2CSniffer
import RPi.GPIO as GPIO

SDA = 2
SCL = 3
GPIO_TRIGGER = 4

def print_func(frame):
        print("pyro: " + frame)
        
i2c_sniffer = I2CSniffer(SDA, SCL, print_func)
i2c_sniffer.sniff()

while True:
        time.sleep(1)
        


class Pyrometer:
    def __init__(self):
        self.i2c_sniffer = I2CSniffer(SDA, SCL, self._cb)
        self.gpio_trigger = GPIO_TRIGGER

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
        time.sleep(3)
        self.i2c_sniffer.stop()
        for frame in self.frames):
            print("* " + frame)

        

        
        
        

