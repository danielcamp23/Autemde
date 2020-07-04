from PyQt5.QtCore import QThread, pyqtSignal
from typing import Callable

from src.id_scanner import IDScanner
from src.telescopic_detector import TelescopicDetector
from src.pyrometer import Pyrometer
from src.mqtt_client import MQTTClient
from src.io_sensors import IoSensors
from src.actuator import Actuator

IN_SENSOR = 2
OUT_SENSOR = 3
FACE_SENSOR = 4
HANDS_SENSOR = 5

class EState(enum.enum):
    Iddle = 0
    DetectCard = 1
    DetectFace = 2
    ApproachFace = 3
    TakeTemperature = 4
    DetectHands = 5
    WashHands = 6
    OpenDoor = 7

class EEvent(enum.Enum):
    NOOP = 0
    PersonInDetected = 1
    PersonOutDetected = 1
    CardDetected = 2
    CardNotDetected = 2
    FaceDetected = 3
    FaceNotDetected = 3
    FaceApproached = 4
    FaceNotApproached = 4
    TemperatureTaken = 5
    TemperatureNotTaken = 5
    TemperatureNotTaken
    HandsDetected = 6
    HandsRemoved
    HandsNotDetected
    HandsWashed = 7
    DoorOpen = 8
    DoorClosed = 9

class State(object):
    def __init__(self):
        pass

    def on_event(self, go_to_next):
        pass

    def next_state(self):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__


class IddleState(State):
    def __init__(self):
        super().__init__()

    def on_event(self, go_to_next):
        if go_to_next:
            return DetectCardState()
        else:
            return self

    def next_state(self):
        return DetectCardState()

class ErrorState(State):
    def __init__(self):
        super().__init__()

    def on_event(self, go_to_next):
        return self

    def next_state(self):
        return DetectCardState()

class DetectCardState(State):
    def on_event(self, go_to_next):
        if go_to_next:
            return DetectFaceState()
        else:
            return self

    def next_state(self):
        return DetectFaceState()            

class DetectFaceState(State):
    def on_event(self, go_to_next):
        if go_to_next:
            return ApproachFaceState()
        else:
            return self

    def next_state(self):
        return ApproachFaceState()              

class ApproachFaceState(State):
    def on_event(self, go_to_next):
        if go_to_next:
            return TakeTemperatureState()
        else:
            return self

    def next_state(self):
        return TakeTemperatureState()             

class TakeTemperatureState(State):
    def on_event(self, event):
        if event == EEvent.TemperatureTaken:
            return DetectHandsState()
        else:
            return self

    def next_state(self):
        return DetectHandsState()             

class DetectHandsState(State):
    def on_event(self, event):
        if event == EEvent.HandsDetected:
            return WashHandsState()
        else:
            return self

    def next_state(self):
        return WashHandsState()            

class WashHandsState(State):
    def on_event(self, event):
        if event == EEvent.HandsWashed:
            return OpenDoorState()
        elif event == EEvent.HandsRemoved:
            return WashHandsPauseState()
        else:
            return self

    def next_state(self):
        return OpenDoorState()

class WashHandsPauseState(State):
    def on_event(self, event):
        if event == EEvent.HandsDetected:
            return WashHandsState()
        else:
            return self

    def next_state(self):
        return OpenDoorState()                

class OpenDoorState(State):
    def on_event(self, event):
        if event == EEvent.PersonOutDetected:
            return IddleState
        else:
            return self 

    def next_state(self):
        return IddleState()                                                                          

class StateMachine:
    def __init__(self, cb : Callable[[State, State], None]):
        self.state = IddleState()
        self.change_cb = cb

    def get_current_state(self):
        return self.state

    def process_event(self, event):
        previous_state = self.state

        if self.state == 'IddleState' and event == EEvent.PersonInDetected:
            self.state = self.state.next_state()
        elif self.state == 'DetectCardState':
            if event == EEvent.CardDetected:
                self.state = self.state.next_state()
            elif event == EEvent.CardNotDetected:
                self.state = ErrorState()
        elif self.state == "DetectFaceState":
            if event == EEvent.FaceDetected:
                self.state = self.state.next_state()
            elif event == EEvent.FaceNotDetected:
                self.state = ErrorState()
        elif self.state == "ApproachFaceState":
            if event == EEvent.FaceApproached:
                self.state = self.state.next_state()
            elif event == EEvent.FaceNotApproached:
                self.state = ErrorState()
        elif self.state == "TakeTemperatureState":
            if event == EEvent.TemperatureTaken:
                self.state = self.state.next_state()
            elif event == EEvent.TemperatureNotTaken:
                self.state = ErrorState()
        elif self.state == "DetectHandsState":
            if event == EEvent.HandsDetected:
                self.state = self.state.next_state()
            elif event == EEvent.HandsNotDetected:
                self.state = ErrorState()
        elif self.state == "WashHandsState":
            if event == EEvent.HandsWashed:
                self.state = self.state.next_state()
        elif self.state == "OpenDoorState":
            if event == EEvent.PersonOutDetected:
                self.state = self.state.next_state()

        if self.state != previous_state:
            #There was a change in the state
            #Notify to SM owner
            self.change_cb(previous_state, self.state)

class MainThread(QThread):
    def __init__(self):
        super().__init__()

        self.is_person_detected = False
        self.is_card_detected = False
        self.is_face_detected = False
        self.is_temperature_taken = False
        self.is_to_wash_hands = False
        self.init_action = False

        self.state_machine = StateMachine(self.on_state_machine_change)

        self.temperature = 0.0
        self.id_fields = list()
        
        #Input modules
        self.id_scanner = IDScanner(self.id_card_detected)
        self.telescopic_detector = TelescopicDetector(self.telescopic_action)
        self.pyrometer = Pyrometer(self.temperature_taken)

        self.sensors = IoSensors()
        self.register_sensor_callbacks()

        #Output modules
        MOTOR_GPIO = 10
        self.door_motor = Actuator(MOTOR_GPIO, self.)
        
        HANDS_GPIO = 11
        self.hands_cleaner = Actuator(HANDS_GPIO)

        #Report modules
        self.mqtt_client = MQTTClient()
        #FLASK server


    def register_sensor_callbacks(self):
        self.sensors.register_callback(IN_SENSOR, "Person In Detected", self.sensor_triggered)
        self.sensors.register_callback(OUT_SENSOR, "Person Out Detected", self.sensor_triggered)
        self.sensors.register_callback(FACE_SENSOR, "Face Detected", self.sensor_triggered)
        self.sensors.register_callback(HANDS_SENSOR, "Hands Detected", self.sensor_triggered)
       
    def run(self):
        self.id_scanner.stop()
        self.id_scanner.stop()
        while True:
            current_state = self.state_machine.get_current_state()
            if current_state == 'IddleState':
                pass
            elif current_state == 'DetectCardState':
                self.id_scanner.start()
            elif current_state == 'DetectFaceState':
                self.id_scanner.stop()
                self.telescopic_detector.detect()
            elif current_state == 'ApproachFaceState':
                #action to approach to person's face
                pass
            elif current_state == 'TakeTemperatureState':
                self.pyrometer.measure()
            else:
                pass
            #elif current_state == 'DetectHandsState':

            time.sleep(2)

    def id_card_detected(self, frame):
        print(frame)
        fields = frame.split(',')
        self.id_fields = list()

        for field in fields:
            filtered = filter(lambda x: x in string.printable, field)
            str_ = ""
            f = str_.join(filtered).strip()
            self.id_fields.append(f)

        self.state_machine.process_event(EEvent.CardDetected)            

    def temperature_taken(self, temperature):
        if temperature > 0:
            print("temperature taken")
            self.temperature = temperature
            self.state_machine.process_event(EEvent.TemperatureTaken)
        else:
            print("failed taking temperature")
            self.state_machine.process_event(EEvent.TemperatureNotTaken)

    def sensor_triggered(self, gpio: int, level: int, tick: int):
        if gpio == IN_SENSOR:
            self.state_machine.process_event(EEvent.PersonInDetected)
        elif gpio == OUT_SENSOR:
            self.state_machine.process_event(EEvent.PersonOutDetected)
        elif gpio == FACE_SENSOR:
            self.state_machine.process_event(EEvent.FaceApproached)
        elif gpio == HANDS_SENSOR:
            if level == 1:
                self.state_machine.process_event(EEvent.HandsDetected)
            else:
                self.state_machine.process_event(EEvent.HandsRemoved)
        else:
            pass

    def telescopic_action(self, telescopic_aligned):
        if telescopic_aligned:
            print("Telescopic in position")
            self.state_machine.process_event(EEvent.FaceDetected)
        else:
            print("Telescopic failed!")
            self.state_machine.process_event(EEvent.FaceNotDetected)

    def on_state_machine_change(self, previous_state: State, current_state: State):
        if current_state == ErrorState():
            if previous_state == DetectCardState():
                #card was not detected
                pass
            elif previous_state == DetectFaceState():
                #face was not detected
                pass
            elif previous_state == ApproachFaceState():
                #face not approached
                pass
            elif previous_state == TakeTemperatureState():
                #fail to take temperature
                pass
        else:
            if current_state == DetectCardState():
                self.id_scanner.start()
            elif current_state == DetectFaceState():
                self.id_scanner.stop()
                self.telescopic_detector.start()
            elif current_state == ApproachFaceState():
                self.telescopic_detector.stop()
                #start face motor
            elif current_state == TakeTemperatureState():
                #stop face motor
                self.pyrometer.start()
            elif current_state == DetectHandsState():
                self.pyrometer.stop()
            elif current_state == WashHandsState():
                self.hands_cleaner.start()
            elif current_state == OpenDoorState():
                #open door
                STEPS = 100
                self.door_motor.move_right(STEPS)
            elif current_state == IddleState():
                STEPS = 100
                self.door_motor.move_left(STEPS)
        