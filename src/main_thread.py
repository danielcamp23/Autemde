from PyQt5.QtCore import QThread, pyqtSignal

from src.id_scanner import IDScanner
from src.telescopic_detector import TelescopicDetector
from src.pyrometer import Pyrometer
from src.mqtt_client import MQTTClient

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
    PersonDetected = 1
    CardDetected = 2
    FaceDetected = 3
    FaceNotDetected = 3
    FaceApproached = 4
    TemperatureTaken = 5
    TemperatureNotTaken
    HandsDetected = 6
    HandsWashed = 7
    DoorOpen = 8
    DoorClosed = 9

class State(object):
    def __init__(self):
        pass

    def on_event(self, event):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__


class IddleState(State):
    def __init__(self):
        super().__init__()

    def on_event(self, event):
        if event == EEvent.PersonDetected:
            return DetectCardState()
        else:
            return self

class DetectCardState(State):
    def on_event(self, event):
        if event == EEvent.CardDetected:
            return DetectFaceState()
        else:
            return self

class DetectFaceState(State):
    def on_event(self, event):
        if event == EEvent.FaceDetected:
            return ApproachFaceState()
        else:
            return self

class ApproachFaceState(State):
    def on_event(self, event):
        if event == EEvent.FaceApproached:
            return TakeTemperatureState()
        else:
            return self

class TakeTemperatureState(State):
    def on_event(self, event):
        if event == EEvent.TemperatureTaken:
            return DetectHandsState()
        else:
            return self 

class DetectHandsState(State):
    def on_event(self, event):
        if event == EEvent.HandsDetected:
            return WashHandsState()
        else:
            return self

class WashHandsState(State):
    def on_event(self, event):
        if event == EEvent.HandsWashed:
            return OpenDoorState()
        else:
            return self  

class OpenDoorState(State):
    def on_event(self, event):
        if event == EEvent.DoorOpen:
            return IddleState
        else:
            return self                                                              

class StateMachine:
    def __init__(self):
        self.state = IddleState()
        self.signal = pyqtSignal(EState)

    def get_current_state():
        return self.state

    def process_event(self, flag):
        if self.state == 'IddleState':
            self.state = self.state.on_event(True)
        elif self.state == 'DetectCard':
            self.state = self.state.on_event(True)

    def on_state_changed(self):
        pass

class MainThread(QThread):
    def __init__(self):
        super().__init__()

        self.is_person_detected = False
        self.is_card_detected = False
        self.is_face_detected = False
        self.is_temperature_taken = False
        self.is_to_wash_hands = False
        self.init_action = False

        self.state_machine = StateMachine()

        self.temperature = 0.0
        self.id_fields = list()
        
        self.id_scanner = IDScanner(self.id_card_detected)
        self.telescopic_detector = TelescopicDetector(self.telescopic_action)
        self.pyrometer = Pyrometer(self.temperature_taken)
        self.mqtt_client = MQTTClient()
       
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

    def temperature_taken(self, temperature):
        if temperature > 0:
            print("temperature taken")
            self.temperature = temperature
            self.state_machine.process_event(EEvent.TemperatureTaken)
        else:
            print("failed taking temperature")
            self.state_machine.process_event(EEvent.TemperatureNotTaken)

    def __sensor_triggered(self, gpio, level):
        if gpio == IN_SENSOR:
            self.__state_machine.process_event(EEvent.PersonDetected)

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

    def telescopic_action(self, telescopic_aligned):
        if telescopic_aligned:
            print("Telescopic in position")
            self.state_machine.process_event(EEvent.FaceDetected)
        else:
            print("Telescopic failed!")
            self.state_machine.process_event(EEvent.FaceNotDetected)