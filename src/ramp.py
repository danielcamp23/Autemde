'''
A ramp is composed by two segments: 
1. The ramp itself
2. A flat region

After the ramp has been reached, the flat region will become active
'''

class Ramp:
    def __init__(self, in_ramp_width):
        self.max_ramp_width = in_ramp_width # max width of acceleration/deacceleration in steps

    # Returns duple: (ramp_width, flat_width)
    # Returns (steps_to_accelerate, flat_steps, steps_to_deaccelerate)
    def calc_width(self, in_steps_to_take, in_current_step_on_ramp):
        if in_current_step_on_ramp == 0: # The movement is about to start
            if in_steps_to_take <= self.max_ramp_width:
                steps_to_acccelerate = in_steps_to_take / 2
                steps_to_deaccelerate = in_steps_to_take / 2
                steps_flat = 0
                return (int(steps_to_acccelerate), int(steps_flat), int(steps_to_deaccelerate))
            
            elif self.max_ramp_width < in_steps_to_take and in_steps_to_take <= self.max_ramp_width * 2:
                steps_to_acccelerate = in_steps_to_take / 2
                steps_to_deaccelerate = in_steps_to_take / 2
                steps_flat = 0
                return (int(steps_to_acccelerate), int(steps_flat), int(steps_to_deaccelerate))
            
            else: # in_steps_to_take > self.max_ramp_width * 2
                steps_to_acccelerate = self.max_ramp_width
                steps_to_deaccelerate = self.max_ramp_width
                steps_flat = in_steps_to_take - 2 * self.max_ramp_width              
                return (int(steps_to_acccelerate), int(steps_flat), int(steps_to_deaccelerate))
        
        elif in_current_step_on_ramp > 0 and in_current_step_on_ramp < self.max_ramp_width: # It is accelerating/deaccelerating already
            if in_steps_to_take <= in_current_step_on_ramp:
                steps_to_acccelerate = 0
                steps_to_deaccelerate = in_current_step_on_ramp
                steps_flat = 0                 
                return (int(steps_to_acccelerate), int(steps_flat), int(steps_to_deaccelerate))
            
            elif in_current_step_on_ramp < in_steps_to_take and in_steps_to_take <= 2 * self.max_ramp_width - in_current_step_on_ramp:
                peak = (in_steps_to_take + in_current_step_on_ramp) / 2
                steps_to_acccelerate = peak - in_current_step_on_ramp
                steps_to_deaccelerate = peak
                steps_flat = 0                   
                return (int(steps_to_acccelerate), int(steps_flat), int(steps_to_deaccelerate))
            
            else: # in_steps_to_take >  2 * self.max_ramp_width - in_current_step_on_ramp
                steps_to_acccelerate = self.max_ramp_width - in_current_step_on_ramp
                steps_to_deaccelerate = self.max_ramp_width
                steps_flat = in_steps_to_take + in_current_step_on_ramp - 2 * self.max_ramp_width              
                return (int(steps_to_acccelerate), int(steps_flat), int(steps_to_deaccelerate))
        
        else: # It is in constant movement
            if in_steps_to_take <= self.max_ramp_width:
                steps_to_acccelerate = 0
                steps_to_deaccelerate = self.max_ramp_width
                steps_flat = 0
                return (int(steps_to_acccelerate), int(steps_flat), int(steps_to_deaccelerate))

            else:
                steps_to_acccelerate = 0
                steps_to_deaccelerate = self.max_ramp_width
                steps_flat = in_steps_to_take - self.max_ramp_width
                return (int(steps_to_acccelerate), int(steps_flat), int(steps_to_deaccelerate))
