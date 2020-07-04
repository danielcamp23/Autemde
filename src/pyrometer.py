import RPi.GPIO as GPIO 
import time
from .i2c_sniffer import I2CSniffer
import .utilities.time_guard
import RPi.GPIO as GPIO

SDA = 2
SCL = 3
GPIO_TRIGGER = 4
TIMEOUT = 10

class Pyrometer:
    def __init__(self, measure_complete_cb):
        self.measure_complete_cb = measure_complete_cb
        self.i2c_sniffer = I2CSniffer(SDA, SCL, self._cb)
        self.gpio_trigger = GPIO_TRIGGER

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_trigger, GPIO.OUT)
        GPIO.output(self.gpio_trigger, True)

        self.frames = list()

    def _cb(self, frame):
        self.frames.append(frame)

    def start(self):
        temperature = 0.0
        temperature_taken = False
        with time_guard(TIMEOUT):
            while True:
                print("Take temp")
                self.frames = list()
                self.i2c_sniffer.sniff()
                GPIO.output(self.gpio_trigger, False)
                time.sleep(0.5)
                GPIO.output(self.gpio_trigger, True)
                time.sleep(0.5)
                self.i2c_sniffer.stop()

                if len(self.frames) == 3:
                    temperature = self.decode_temperature(self.frames[2])
                    temperature_taken = True
                    break
        
        if temperature_taken:
            self.measure_complete_cb(temperature)
        else:
            self.measure_complete_cb(-1.0)

    def stop(self):
        #dummy method
        pass

    def decode_temperature(self, frame):
        #print("frame: " + frame)
        filtered = filter(lambda x: x != '[' and x != ']', frame)
        s = ""
        filterd_full = s.join(filtered)

        temp_str = "0x" + filterd_full[10] + filterd_full[6] + filterd_full[7]
        temp = int(temp_str, 16) 
        temp_float = temp / 100.0

        return temp_float
        #print("temperature: " + str(temp_float))
        #self._measure_complete_cb(str(temp_float))
        

        
        
        

