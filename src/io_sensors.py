from typing import Callable
import RPi.GPIO as GPIO
import pigpio
#Base class to

class SensorInfo(object):
    def __init__(self, gpio: int, cb_name: str, cb: Callable[[int, int, int], None], cb_handler):
        self.gpio = gpio 
        self.cb_name = cb_name
        self.cb = cb
        self.cb_handler = cb_handler

class IoSensors(object):
    def __init__(self):
        self.pi = pigpio.pi()
        self.sensors = dict()

    def __callback(self, gpio : int, level : int, tick : int):
        sensor = self.sensors[gpio]
        if sensor is not None:
            print(sensor.cb_name)
            sensor.cb()

    def register_callback(self, gpio: int, cb_name: str, cb: Callable[[int, int, int], None]):
        if self.sensors[gpio] is None:
            #initializes
            self.pi.set_mode(gpio, pigpio.INPUT)

            #registers callback
            cb_handler = self.pi.callback(gpio, pigpio.EITHER_EDGE, self.__callback)

            self.sensors[gpio] = SensorInfo(gpio, cb_name, cb, cb_handler)
        

        