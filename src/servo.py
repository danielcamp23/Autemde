#import RPi.GPIO as GPIO
import time
import threading
import enum

from .ramp import Ramp

RAMP_STEPS = 100
MIN_SLEEP = 0.002
MAX_SLEEP = 0.5
STEPS_TO_CHECK_THREAD_FINISH = 2

class Direction(enum.Enum):
    Stop = 0
    Right = 1
    Left = 2

ramp_stepper = Ramp(RAMP_STEPS)

class Servo:
    def __init__(self, in_steps_gpio, in_direction_gpio):
        self.steps_gpio = in_steps_gpio
        self.direction_gpio = in_direction_gpio

        self.current_step_on_ramp = 0
        self.current_direction = Direction.Stop
        self.lock = threading.Lock()
        self.finish_thread = False
        self.threads = list()

    def move_right(self, in_steps_to_take):
        self.move(Direction.Right, in_steps_to_take)

    def move_left(self, in_steps_to_take):
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
        
        self.lock.acquire()
        try:
            current_step_on_ramp = self.current_step_on_ramp
            current_direction = self.current_direction
        finally:
            self.lock.release()

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
            #print("****_steps_to_accelerate " + str(steps_to_accelerate))
            #print("****flat_steps " + str(flat_steps))
            #print("****steps_to_deaccelerate " + str(steps_to_deaccelerate))


        for t in self.threads:
            if t.is_alive():
                print("lock taken")
                self.lock.acquire()
                print("lock Acquired")
                try:
                    self.finish_thread = True
                finally:
                    self.lock.release()
                    t.join() # waits for thread to finish
                    print("Wait finished")

        self.finish_thread = False
        self.threads = list()

        t = threading.Thread(target=self.movement_thread, args=(Direction.Right, steps_to_accelerate, flat_steps, steps_to_deaccelerate,))
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
                #GPIO.output(self.steps_gpio, True)
                print("+step " + str(current_step_on_ramp) + " - " + str(current_direction))
                time.sleep(delay)
                #GPIO.output(self.steps_gpio, False)
                print("-step " + str(current_step_on_ramp) + " - " + str(current_direction))
                time.sleep(delay)

                if lock_ctr % STEPS_TO_CHECK_THREAD_FINISH == 0 and self.is_thread_to_be_finished() == True:
                    print("Finish Thread")

        #Start actual movement
        if in_direction ==  Direction.Right:
            #GPIO.output(self.direction_gpio, True) 
            print()
        else:
            #GPIO.output(self.direction_gpio, False) 
            print()

        lock_ctr = 0
        starting_step = current_step_on_ramp
        print("starting_step " + str(starting_step))
        print("in_steps_to_accelerate " + str(in_steps_to_accelerate))
        for i in range(starting_step, in_steps_to_accelerate, 1):
            current_direction = in_direction
            current_step_on_ramp = i
            lock_ctr += 1
            delay = self.get_delay_for_step(current_step_on_ramp)
            #GPIO.output(self.steps_gpio, True)
            print("+step " + str(current_step_on_ramp) + " - " + str(current_direction))
            time.sleep(delay)
            #GPIO.output(self.steps_gpio, False)
            print("-step " + str(current_step_on_ramp) + " - " + str(current_direction))
            time.sleep(delay)

            if lock_ctr % STEPS_TO_CHECK_THREAD_FINISH == 0 and self.is_thread_to_be_finished() == True:
                print("Finish Thread")

        lock_ctr = 0
        for _ in range(in_flat_steps):
            current_direction = in_direction
            lock_ctr += 1
            delay = self.get_delay_for_step(RAMP_STEPS)
            #GPIO.output(self.steps_gpio, True)
            print("+step " + str(current_step_on_ramp) + " - " + str(current_direction))
            time.sleep(delay)
            #GPIO.output(self.steps_gpio, False)
            print("-step " + str(current_step_on_ramp) + " - " + str(current_direction))
            time.sleep(delay)

            if lock_ctr % STEPS_TO_CHECK_THREAD_FINISH == 0 and self.is_thread_to_be_finished() == True:
                print("Finish Thread")

        starting_step = current_step_on_ramp 
        for i in reversed(range(starting_step)):
            current_direction = in_direction
            current_step_on_ramp = i
            lock_ctr += 1
            delay = self.get_delay_for_step(current_step_on_ramp)
            #GPIO.output(self.steps_gpio, True)
            print("+step " + str(current_step_on_ramp) + " - " + str(current_direction))
            time.sleep(delay)
            #GPIO.output(self.steps_gpio, False)
            print("-step " + str(current_step_on_ramp) + " - " + str(current_direction))
            time.sleep(delay)

            if current_direction == 0:
                current_direction = Direction.Stop            

            if lock_ctr % STEPS_TO_CHECK_THREAD_FINISH == 0 and self.is_thread_to_be_finished() == True:
                print("Finish Thread")

        print("Movement Finished")
        
        self.lock.acquire()
        try:
            self.current_step_on_ramp = current_step_on_ramp
            self.current_direction = current_direction
        finally:
            self.lock.release() 


    def get_delay_for_step(self, in_current_step_on_ramp):
        slope = (MIN_SLEEP - MAX_SLEEP) / RAMP_STEPS
        return slope * (in_current_step_on_ramp - RAMP_STEPS) + MIN_SLEEP