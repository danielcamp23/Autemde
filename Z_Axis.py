
import sys
import RPi.GPIO as gpio  # https://pypi.python.org/pypi/RPi.GPIO more info
import time

try:
    direction = sys.argv[1]
    steps = int(float(sys.argv[2]))
except:
    steps = 0

gpio.setmode(gpio.BCM)

gpio.setup(14, gpio.OUT)
gpio.setup(15, gpio.OUT)

if direction == 'left':
    gpio.output(14, True)
elif direction == 'right':
    gpio.output(14, False)

StepCounter = 0


WaitTime = 0.05
Desacc = 0.005

def acceleration (step, T_Steps, acc_init, desacc):
    if T_Steps > 84:
        if step <= 42:
            acc_init /= 1.08
        elif (T_Steps - step) <= 42:
            acc_init /= 0.92
        else:
            acc_init = 0.002
    else:
        if step < (T_Steps/2):
            acc_init /= 1.08
        else:
            acc_init /= 0.92
    return acc_init

while StepCounter < steps:
    # turning the gpio on and off tells the easy driver to take one step
    gpio.output(15, True)
    gpio.output(15, False)
    StepCounter += 1

    # Wait before taking the next step...this controls rotation speed
    WaitTime = acceleration (StepCounter, steps, WaitTime, Desacc)
    print (WaitTime)
    time.sleep(WaitTime)

gpio.cleanup()


