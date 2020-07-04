import RPi.GPIO as GPIO

class Actuator(object):
    def __init__(self, gpio: int):
        self.gpio = gpio
        GPIO.setup(gpio, GPIO.OUT)

    def start(self):
        GPIO.output(self.gpio, True)

    def stop(self):
        GPIO.output(self.gpio, False)

