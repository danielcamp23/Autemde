# USAGE
# python pi_detect_drowsiness.py --cascade haarcascade_frontalface_default.xml --shape-predictor shape_predictor_68_face_landmarks.dat
# python pi_detect_drowsiness.py --cascade haarcascade_frontalface_default.xml --shape-predictor shape_predictor_68_face_landmarks.dat --alarm 1

# import the necessary packages
import cv2
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import imutils
import time
import dlib
from src.servo import Servo


# grab the indexes of the facial landmarks for the left and
# right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

TIMEOUT = 30
STEPS_GPIO = 15
DIRECTION_GPIO = 14

def raise_timeout(signum, frame):
	raise TimeoutError

@contextmanager
def time_guard(timeout):

	#Register the signal
	signal.signal(signal.SIGALRM, raise_timeout)
	signal.alarm(timeout)

	try:
		yield
	except:
		pass
	finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
		signal.alarm(0)
    	signal.signal(signal.SIGALRM, signal.SIG_IGN)


class TelescopicDetector:
	def __init__(self):
		self.z_servo =  Servo(in_steps_gpio=STEPS_GPIO, in_direction_gpio=DIRECTION_GPIO)

		# load OpenCV's Haar cascade for face detection (which is faster than
		# dlib's built-in HOG detector, but less accurate), then create the
		# facial landmark predictor
		self.detector = cv2.CascadeClassifier("models/haarcascade_frontalface_default.xml")
		self.predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")

	def detect(self):
		telescopic_aligned = False
		with time_guard(TIMEOUT):
			vs = cv2.VideoCapture(0)
			time.sleep(1.0)

			while True:
				# vs = VideoStream(usePiCamera=True).start()
				_, frame = self.vs.read()
				if frame == None:
					break
				
				#frame = imutils.resize(frame, width=450)
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

				# detect faces in the grayscale frame
				rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

				# loop over the face detections
				for (x, y, w, h) in rects:
					# construct a dlib rectangle object from the Haar cascade
					# bounding box
					rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))

					# determine the facial landmarks for the face region, then
					# convert the facial landmark (x, y)-coordinates to a NumPy
					# array

					shape = predictor(gray, rect)
					shape = face_utils.shape_to_np(shape)

				
					# extract the left and right eye coordinates, then use the
					# coordinates to compute the eye aspect ratio for both eyes
					leftEye = shape[lStart:lEnd]
					rightEye = shape[rStart:rEnd]
				
					delt = leftEye[3][1] - 240
					print("delta = " + str(delt))      
					if delt < -20:
						self.z_servo.move_left(abs(delt*4))
					elif delt > 20:
						self.z_servo.move_right(abs(delt*4))
					else:
						self.z_servo.stop()
						telescopic_aligned = True
						break

					# compute the convex hull for the left and right eye, then
					# visualize each of the eyes
					leftEyeHull = cv2.convexHull(leftEye)
					rightEyeHull = cv2.convexHull(rightEye)
					cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
					cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

				# show the frame
				cv2.imshow("Frame", frame)
				key = cv2.waitKey(30) & 0xFF
			
				# if the `q` key was pressed, break from the loop
				if key == ord("q"):
					break

			# do a bit of cleanup
			cv2.destroyAllWindows()
			vs.stop()
			return telescopic_aligned

