import time

from src.ramp import Ramp 
from src.servo import Servo

my_ramp = Ramp(200)

steps_to_take = 10
current_step_on_ramp = 90

(steps_to_accelerate, flat_steps, steps_to_deaccelerate) = my_ramp.calc_width(steps_to_take, current_step_on_ramp)
print("Current pos: " + str(current_step_on_ramp)) 
print("steps_to_take: " + str(steps_to_take)) 

#print("Subiendo: " + str(steps_to_accelerate))
#print("Plano: " + str(flat_steps))
#print("Bajando: " + str(steps_to_deaccelerate))

my_servo = Servo(10, 12)


my_servo.move_right(steps_to_take)

time.sleep(2)

my_servo.move_left(steps_to_take)





