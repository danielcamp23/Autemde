# USAGE
# python pi_detect_drowsiness.py --cascade haarcascade_frontalface_default.xml --shape-predictor shape_predictor_68_face_landmarks.dat
# python pi_detect_drowsiness.py --cascade haarcascade_frontalface_default.xml --shape-predictor shape_predictor_68_face_landmarks.dat --alarm 1

# import the necessary packages
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import os
from src.servo import Servo


servo_z_axis = Servo(in_steps_gpio=15, in_direction_gpio=14)
servo_x_axis = Servo(in_steps_gpio=27, in_direction_gpio=17)

servo_z_axis.move_left(1000)
