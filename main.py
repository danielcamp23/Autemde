import time

#from src.ramp import Ramp 
#from src.servo import Servo
#from src.id_detector import IDDetector
from src.pyrometer import Pyrometer

if __name__ == "__main__":
    pyrometer = Pyrometer()

    while True:
        pyrometer.measure()
        time.sleep(3)







