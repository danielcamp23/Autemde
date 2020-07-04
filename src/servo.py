#import RPi.GPIO as GPIO
import time
import threading
import enum

import sys
import RPi.GPIO as GPIO  # https://pypi.python.org/pypi/RPi.GPIO more info

from .ramp import Ramp

RAMP_STEPS = 40
MIN_SLEEP = 0.002
MAX_SLEEP = 0.05
STEPS_TO_CHECK_THREAD_FINISH = 5

class Direction(enum.Enum):
    Stop = 0
    Right = 1
    Left = 2

ramp_stepper = Ramp(RAMP_STEPS)

class Servo:
    def __init__(self, in_steps_gpio: int, in_direction_gpio: int):
        self.current_step_on_ramp = 0
        self.current_direction = Direction.Stop
        self.lock = threading.Lock()
        self.finish_thread = False
        self.threads = list()
        self.threads2 = list()
        
        #Initialize gpio
        self.steps_gpio = in_steps_gpio
        self.direction_gpio = in_direction_gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(in_steps_gpio, GPIO.OUT)
        GPIO.setup(in_direction_gpio, GPIO.OUT)

    def move_right(self, in_steps_to_take: int):
        
        self.move(Direction.Right, in_steps_to_take)

    def move_left(self, in_steps_to_take: int):
        self.move(Direction.Left, in_steps_to_take)

    def stop(self):
        self.lock.acquire()
        try:
            current_step_on_ramp = self.current_step_on_ramp
            current_direction = self.current_direction
        finally:
            self.lock.release()

        self.move(current_direction, current_step_on_ramp)                   

    def move(self, in_direction, in_steps_to_take):
        current_step_on_ramp = 0
        current_direction = Direction.Stop
        lock_taken = False
        
        lock_taken = self.lock.acquire(blocking=True, timeout=0.1)
        try:
            if lock_taken:
                current_step_on_ramp = self.current_step_on_ramp
                current_direction = self.current_direction
        finally:
            if lock_taken:
                self.lock.release()
            else:
                return
            

        steps_to_accelerate = 0
        flat_steps = 0
        steps_to_deaccelerate = 0

        #print("current: " + str(current_direction))
        #print("to: " + str(in_direction))
        if current_direction == Direction.Left:
            (_, _, steps_to_deaccelerate_to_stop) = ramp_stepper.calc_width(0, current_step_on_ramp)
            #.... keeps moving left to stop -- steps_to_deaccelerate

            #start moving to the right
            # should get current_step_on_ramp again
            # The total number of steps will be the deaccelerated ones + the in_steps_to_take
            (steps_to_accelerate, flat_steps, steps_to_deaccelerate) = ramp_stepper.calc_width(steps_to_deaccelerate_to_stop + in_steps_to_take, current_step_on_ramp)

        else:
            (steps_to_accelerate, flat_steps, steps_to_deaccelerate) = ramp_stepper.calc_width(in_steps_to_take, current_step_on_ramp)
            print("****_steps_to_accelerate " + str(steps_to_accelerate))
            print("****flat_steps " + str(flat_steps))
            print("****steps_to_deaccelerate " + str(steps_to_deaccelerate))


        for t in self.threads:
            if t.is_alive():
                lock_taken = self.lock.acquire(blocking=True, timeout=0.1)
                try:
                    if lock_taken:
                        self.finish_thread = True
                finally:
                    if lock_taken:
                        self.lock.release()
                        t.join() # waits for thread to finish
                    else:
                        print("Wait finished")
                        return

        self.finish_thread = False
        self.threads = list()

        t = threading.Thread(target=self.movement_thread, args=(in_direction, steps_to_accelerate, flat_steps, steps_to_deaccelerate,))
        self.threads.append(t)
        self.threads[0].start()

    def is_thread_to_be_finished(self):
        finish_thread = False
        acquired = self.lock.acquire(blocking=False, timeout=-1)
        try:
            if acquired:
                finish_thread = self.finish_thread
        finally:
            if acquired:
                self.lock.release()

        return finish_thread


    def movement_thread(self, in_direction, in_steps_to_accelerate, in_flat_steps, in_steps_to_deaccelerate):
        current_step_on_ramp = 0
        current_direction = Direction.Stop
        finish_thread = False

        print("Thread Started")


        acquired = self.lock.acquire(blocking=True, timeout=1) # waits for 1 second
        try:
            if acquired:
                current_step_on_ramp = self.current_step_on_ramp
                current_direction = self.current_direction
        finally:
            if acquired:
                self.lock.release() 
            else:
                return  

        # Needs to invert direction
        if current_direction != in_direction and current_direction != Direction.Stop:
            
            #Stop first
            lock_ctr = 0
            starting_step = current_step_on_ramp
            for i in reversed(range(starting_step)):
                current_step_on_ramp = i
                lock_ctr += 1
                delay = self.get_delay_for_step(current_step_on_ramp)
                GPIO.output(self.steps_gpio, True)
                #print("+step " + str(current_step_on_ramp) + " - " + str(current_direction))
                #time.sleep(delay)
                GPIO.output(self.steps_gpio, False)
                #print("-step " + str(current_step_on_ramp) + " - " + str(current_direction))
                time.sleep(delay)

                if lock_ctr % STEPS_TO_CHECK_THREAD_FINISH == 0 and self.is_thread_to_be_finished() == True:
                    print("Finish Thread")
                    in_steps_to_accelerate = 0
                    in_flat_steps = 0
                    in_steps_to_accelerate = 0
                    finish_tread = True
                    break

        
        if finish_thread != True:
            #Start actual movement
            if in_direction ==  Direction.Right:
                GPIO.output(self.direction_gpio, True) 
            else:
                GPIO.output(self.direction_gpio, False) 

            lock_ctr = 0
            starting_step = current_step_on_ramp
            print("starting_step " + str(starting_step))
            print("in_steps_to_accelerate " + str(in_steps_to_accelerate))
            for i in range(starting_step, in_steps_to_accelerate):
                current_direction = in_direction
                current_step_on_ramp = i
                lock_ctr += 1
                delay = self.get_delay_for_step(current_step_on_ramp)
                GPIO.output(self.steps_gpio, True)
                #print("+step " + str(current_step_on_ramp) + " - " + str(current_direction))
                #time.sleep(delay)
                GPIO.output(self.steps_gpio, False)
                #print("-step " + str(current_step_on_ramp) + " - " + str(current_direction))
                time.sleep(delay)

                if lock_ctr % STEPS_TO_CHECK_THREAD_FINISH == 0 and self.is_thread_to_be_finished() == True:
                    print("Finish Thread")
                    finish_thread = True
                    break

        lock_ctr = 0
        
        if finish_thread != True:
            for i in range(in_flat_steps):
                current_direction = in_direction
                lock_ctr += 1
                delay = self.get_delay_for_step(RAMP_STEPS)
                GPIO.output(self.steps_gpio, True)
                #print("+step " + str(current_step_on_ramp + i) + " - " + str(current_direction))
                #time.sleep(delay)
                GPIO.output(self.steps_gpio, False)
                #print("-step " + str(current_step_on_ramp + i) + " - " + str(current_direction))
                time.sleep(delay)

                if lock_ctr % STEPS_TO_CHECK_THREAD_FINISH == 0 and self.is_thread_to_be_finished() == True:
                    print("Finish Thread")
                    finish_thread = True
                    break

        if finish_thread != True:
            starting_step = current_step_on_ramp 
            for i in reversed(range(starting_step)):
                current_direction = in_direction
                current_step_on_ramp = i
                lock_ctr += 1
                delay = self.get_delay_for_step(current_step_on_ramp)
                GPIO.output(self.steps_gpio, True)
                #print("+step " + str(current_step_on_ramp) + " - " + str(current_direction))
                #time.sleep(delay)
                GPIO.output(self.steps_gpio, False)
                #print("-step " + str(current_step_on_ramp) + " - " + str(current_direction))
                time.sleep(delay)

                if current_direction == 0:
                    current_direction = Direction.Stop            

                if lock_ctr % STEPS_TO_CHECK_THREAD_FINISH == 0 and self.is_thread_to_be_finished() == True:
                    print("Finish Thread")
                    finish_thread = True
                    break

        print("Movement Finished")
        
        self.lock.acquire()
        try:
            self.current_step_on_ramp = current_step_on_ramp
            self.current_direction = current_direction
        finally:
            self.lock.release() 


    def get_delay_for_step(self, in_current_step_on_ramp):
        slope = (MIN_SLEEP - MAX_SLEEP) / RAMP_STEPS
        return slope * (in_current_step_on_ramp) + MAX_SLEEP
