import cv2
import numpy as np
import time
import threading
from PIL import Image
from imutils.video import VideoStream
import os
from .ramp import Ramp

from .autofocus import Autofocus


xROI = 70
yROI = 80
wROI = 500
hROI = 320

VIDEO_FRAME_WIDTH   = 640
VIDEO_FRAME_HEIGHT  = 480
SCREENSHOT_WIDTH    = 2592
SCREENSHOT_HEIGHT   = 1944

class IDDetector:
    def __init__(self):
        self.vs = cv2.VideoCapture(0)#
        self.vs.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_FRAME_WIDTH)
        #self.vs.resolution = (VIDEO_FRAME_WIDTH, VIDEO_FRAME_HEIGHT)
        self.vs.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_FRAME_HEIGHT)
        self.t = threading.Thread(target=self.detection_thread, args=())

    def start_detection(self):
        #self.vs.start()
        time.sleep(1.0)
        self.t.start()


    def stop_detection(self):
        print("")

    def detection_thread(self):
        while True:
            _, frame = self.vs.read()
            self.draw_roi(frame)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            roi = self.get_roi_image(gray_frame) #Extracts ROI
            roi = self.filter_image(roi) #Apply bilateral filter to gray ROI

            canny_image = self.detect_lines(roi)
            gradient_image = self.get_gradient_image(roi)

            contours = self.get_contours(gradient_image, frame)

            # Verify if id card is in place
            
            if self.process_contours(contours, frame) == False:
                if cv2.waitKey(30) & 0xFF == ord("q"):
                    break
                    
                continue
            
                
            

            #closed_image = self.close_image(grad)

            cv2.imshow('Frame', frame)
            cv2.imshow('Canny', canny_image)
            cv2.imshow('Gradient', gradient_image)
            #cv2.imshow('closed_image', closed_image)
            #if match_id_card(lines_image):
                
            if cv2.waitKey(30) & 0xFF == ord("q"):
                break

        self.vs.release()
        cv2.destroyAllWindows()

    def filter_image(self, img):
        gray = cv2.bilateralFilter(img, 10, 17, 17) #Blur to reduce noise
        return gray

    def detect_lines(self, img):
        ret, _ = cv2.threshold(img,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        canny = cv2.Canny(img, threshold1=(ret*0.2), threshold2=(ret*0.3))
        return canny 

    def match_id_card(self, img):
        contours = get_contours(img)

        if len(contours) > 0 : 
            print("")
            

    def get_contours(self, img, canvas):
        keepers = []
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
       

        for index_, contour_ in enumerate(contours):
            x_, y_, w_, h_ = cv2.boundingRect(contour_)
            b_too_small = w_ < 40 or h_ < 40
            b_wrong_ratio = w_ / h_ < 4
            #b_too_big = h_ > hROI * 0.20 or w_ > wROI * 0.70 or h_/w_ > 0.5
            #b_too_moved = xx > wROI * 0.4 or yy > hROI * 0.7 or yy < hROI * 0.15
            if not b_too_small and not b_wrong_ratio:
                
                #cv2.rectangle(canvas, (x_ + xROI, y_ + yROI), (x_ + w_ + xROI, y_ + h_ + yROI), (255, 0, 0), 1)
                keepers.append([contour_, [x_, y_, w_, h_]])

        return keepers

    def get_gradient_image(self, img):
        gradX = cv2.Sobel(img, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=-1)
        gradY = cv2.Sobel(img, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=-1)

        # subtract the y-gradient from the x-gradient
        gradient = cv2.subtract(gradX, gradY)
        #gradient = cv2.convertScaleAbs(gradient)
        
        gradient = cv2.convertScaleAbs(gradient)

        # blur and threshold the image
        blurred = cv2.blur(gradient, (3, 3))
        (_, thresh) = cv2.threshold(gradient, 200, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 5))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        #cv2.imshow('grad', grad)

        return closed
        #return laplacian

    def close_image(self, img):
        kernel = np.ones((5,5),np.uint8)
        closed_image = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        return closed_image

    def draw_roi(self, img):
        cv2.rectangle(img, (xROI, yROI), (xROI + wROI, yROI + hROI), (255, 0, 0), 5)

    def get_roi_image(self, img):
        return img[yROI:yROI+hROI, xROI:xROI+wROI]

    def process_contours(self, contours, canvas):
        #contour_, [x_, y_, w_, h_]
        if not contours:
            return
        contours.sort(key=lambda entry : entry[1][2], reverse=True)
        print("HOLA")
        candidate = contours[0]
        
        if candidate[1][2] < wROI * 0.6:
            return 
            
        rect = cv2.minAreaRect(candidate[0])
        box = cv2.boxPoints(rect)
        box = np.intp(box) #np.intp: Integer used for indexing (same as C ssize_t; normally either int32 or int64)
        
        box[0][0] += xROI
        box[0][1] += yROI
        box[1][0] += xROI
        box[1][1] += yROI
        box[2][0] += xROI
        box[2][1] += yROI
        box[3][0] += xROI
        box[3][1] += yROI
        cv2.drawContours(canvas, [box], -1, (55, 250, 100))
        
        #cv2.rectangle(canvas, (candidate[1][0] + xROI, candidate[1][1] + yROI), (candidate[1][0] + candidate[1][2] + xROI, candidate[1][1] + candidate[1][3] + yROI), (55, 100, 100), 1)
        #print(contours[0][0])
        self.take_picture(contours[0], box)
            
    def make_low_res(self):
        self.vs.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_FRAME_WIDTH)
        self.vs.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_FRAME_HEIGHT)
        
    def make_high_res(self):
        self.vs.set(cv2.CAP_PROP_FRAME_WIDTH, SCREENSHOT_WIDTH)
        self.vs.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREENSHOT_HEIGHT) 
        
    def take_picture(self, contour, box):
        c = contour
        
        x1,y1,w,h = contour[1]
        x1 += xROI
        y1 += yROI
        
        x2 = x1 + w
        y2 = y1 + h
        
        x1 = x1 * (SCREENSHOT_WIDTH / VIDEO_FRAME_WIDTH)
        x2 = x2 * (SCREENSHOT_WIDTH / VIDEO_FRAME_WIDTH)
        
        y1 = y1 * (SCREENSHOT_HEIGHT / VIDEO_FRAME_HEIGHT)
        y2 = y2 * (SCREENSHOT_HEIGHT / VIDEO_FRAME_HEIGHT)
        
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        
        
        _x1 = box[0][0] * (SCREENSHOT_WIDTH / VIDEO_FRAME_WIDTH)
        _y1 = box[0][1] * (SCREENSHOT_HEIGHT / VIDEO_FRAME_HEIGHT)
        _x2 = box[1][0] * (SCREENSHOT_WIDTH / VIDEO_FRAME_WIDTH)
        _y2 = box[1][1] * (SCREENSHOT_HEIGHT / VIDEO_FRAME_HEIGHT)
        _x3 = box[2][0] * (SCREENSHOT_WIDTH / VIDEO_FRAME_WIDTH)
        _y3 = box[2][1] * (SCREENSHOT_HEIGHT / VIDEO_FRAME_HEIGHT)
        _x4 = box[3][0] * (SCREENSHOT_WIDTH / VIDEO_FRAME_WIDTH)
        _y4 = box[3][1] * (SCREENSHOT_HEIGHT / VIDEO_FRAME_HEIGHT)
        
        self.make_low_res()
        Autofocus.focus(self.vs)
        
        self.make_high_res()
        _, frame = self.vs.read()
        #cv2.imwrite("barcode.jpg", frame[y1:y2, x1:x2, :])
        
        pts1 = np.float32([[_y1, _x1], [_y2, _x2], [_y3, _x3], [_y4, _x4]]) 
        pts2 = np.float32([[0, 0], [400, 0], [0, 240], [400, 240]]) 
      
        # Apply Perspective Transform Algorithm 
        matrix = cv2.getPerspectiveTransform(pts1, pts2) 
        result = cv2.warpPerspective(frame, matrix, (500, 200)) 
    # Wrap the transformed image 
  
        cv2.imshow('frame', frame) # Inital Capture 
        cv2.imshow('frame1', result) # Transformed Capture 

        
        self.make_low_res()
        cv2.namedWindow("Big", cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Big', 600,400)
        cv2.imshow("Big", frame[y1:y2, x1:x2, :])
        cv2.waitKey(0)
        
    def calc_histogram(img, mask):
        hist_mask = cv2.calcHist([img],[0],mask,[256],[0,256])
        return cv2.minMaxLoc(hist_mask)
