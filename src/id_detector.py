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

barcode_ratio = 7.2 / 1.4

VIDEO_FRAME_WIDTH   = 640
VIDEO_FRAME_HEIGHT  = 480
SCREENSHOT_WIDTH    = 2592
SCREENSHOT_HEIGHT   = 1944

PICTURE_RATIO = SCREENSHOT_WIDTH / VIDEO_FRAME_WIDTH

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
            #self.get_contours(canny_image, frame)

            # Verify if id card is in place
            

            
            self.process_contours(contours, frame)
            
            cv2.imshow('Frame', frame)
            cv2.imshow('Canny', canny_image)
            cv2.imshow('Gradient', gradient_image)
            
            if cv2.waitKey(0) & 0xFF == ord("q"):
                break
                    
                #continue
            
                
            

            #closed_image = self.close_image(grad)

            #cv2.imshow('Frame', frame)
            #cv2.imshow('Canny', canny_image)
            
            #cv2.imshow('closed_image', closed_image)
            #if match_id_card(lines_image):

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
       
        contours = sorted(contours, key = cv2.contourArea, reverse = True)[:5]
        
        closed_contours = []

        for contour in contours:
                contour[:,0,0] += xROI
                contour[:,0,1] += yROI
                # approximate the contour
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.015 * perimeter, True)
                if len(approx) == 4:
                        closed_contours.append(approx)
                        
        
        #cv2.drawContours(canvas, contours, -1, (0, 255, 255), 1)
        cv2.drawContours(canvas, closed_contours, -1, (255, 0, 255), 1)
        
        return closed_contours

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

        pts = contours[0].reshape(4, 2)
        #pts *= int(PICTURE_RATIO) # Coordinates for full resolution picture
        
        rect = np.zeros((4, 2), dtype = "float32")
        rect2 = np.zeros((4, 2), dtype = "float32")
        
        # the top-left point has the smallest sum whereas the
        # bottom-right has the largest sum
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        # compute the difference between the points -- the top-right
        # will have the minumum difference and the bottom-left will
        # have the maximum difference
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        rect *= PICTURE_RATIO
        
        rect2 = rect.copy()
        print("rect[0] " + str(rect[0]))
        print("rect[1] " + str(rect[1]))
        print("rect[2] " + str(rect[2]))
        print("rect[3] " + str(rect[3]))
        rect[0] -= 10 
        rect[1][0] += 10 
        rect[1][1] -= 10 
        rect[2] += 10 
        rect[3][0] -= 10 
        rect[3][1] += 10   
        print("rect[0] " + str(rect[0]))      
        print("rect[1] " + str(rect[1]))
        print("rect[2] " + str(rect[2]))
        print("rect[3] " + str(rect[3]))
        
        # now that we have our rectangle of points, let's compute
        # the width of our new image
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        # ...and now for the height of our new image
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        # take the maximum of the width and height values to reach
        # our final dimensions
        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))
        
        # construct our destination points which will be used to
        # map the screen to a top-down, "birds eye" view
        dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]], dtype = "float32")   
        
        self.make_low_res()
        Autofocus.focus(self.vs)
        
        self.make_high_res()
        _, frame = self.vs.read()
        self.make_low_res()
        
        # calculate the perspective transform matrix and warp
        # the perspective to grab the screen
        M = cv2.getPerspectiveTransform(rect, dst)
        warp = cv2.warpPerspective(frame, M, (maxWidth, maxHeight))
        
        cv2.imwrite("barcode.jpg", warp)
        y_min = int(min(rect[0][1], rect[1][1], rect[2][1], rect[3][1]))
        y_max = int(max(rect[0][1], rect[1][1], rect[2][1], rect[3][1]))
        x_min = int(min(rect[0][0], rect[1][0], rect[2][0], rect[3][0]))
        x_max = int(max(rect[0][0], rect[1][0], rect[2][0], rect[3][0]))
        
        y__min = int(min(rect2[0][1], rect2[1][1], rect2[2][1], rect2[3][1]))
        y__max = int(max(rect2[0][1], rect2[1][1], rect2[2][1], rect2[3][1]))
        x__min = int(min(rect2[0][0], rect2[1][0], rect2[2][0], rect2[3][0]))
        x__max = int(max(rect2[0][0], rect2[1][0], rect2[2][0], rect2[3][0]))        
        cv2.imwrite("barcodeno_crop.jpg", frame[y_min:y_max, x_min:x_max, :])
        cv2.imwrite("barcodeno_crop_small.jpg", frame[y__min:y__max, x__min:x__max, :])
        #cv2.drawContours(frame, [rect2], -1, (255, 0, 255), 1)
        #cv2.imshow("crop", frame)
        print("s: " + str(frame.shape))
            
    def make_low_res(self):
        self.vs.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_FRAME_WIDTH)
        self.vs.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_FRAME_HEIGHT)
        
    def make_high_res(self):
        self.vs.set(cv2.CAP_PROP_FRAME_WIDTH, SCREENSHOT_WIDTH)
        self.vs.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREENSHOT_HEIGHT) 
        
    def take_picture(self, contour, box):

        
        
        _x1 = box[0][0] #* (SCREENSHOT_WIDTH / VIDEO_FRAME_WIDTH)
        _y1 = box[0][1] #* (SCREENSHOT_HEIGHT / VIDEO_FRAME_HEIGHT)
        _x2 = box[1][0] #* (SCREENSHOT_WIDTH / VIDEO_FRAME_WIDTH)
        _y2 = box[1][1] #* (SCREENSHOT_HEIGHT / VIDEO_FRAME_HEIGHT)
        _x3 = box[2][0] #* (SCREENSHOT_WIDTH / VIDEO_FRAME_WIDTH)
        _y3 = box[2][1] #* (SCREENSHOT_HEIGHT / VIDEO_FRAME_HEIGHT)
        _x4 = box[3][0] #* (SCREENSHOT_WIDTH / VIDEO_FRAME_WIDTH)
        _y4 = box[3][1] #* (SCREENSHOT_HEIGHT / VIDEO_FRAME_HEIGHT)
        
        self.make_low_res()
        #Autofocus.focus(self.vs)
        
        #self.make_high_res()
        _, frame = self.vs.read()
        #cv2.imwrite("barcode.jpg", frame[y1:y2, x1:x2, :])
        
        pts1 = np.float32([[_x1, _y1], [_x2, _y2], [_x3, _y3], [_x4, _y4]]) 
        pts2 = np.float32([[0, 0], [600, 0], [600, 240], [0, 240]]) 
      
        # Apply Perspective Transform Algorithm 
        matrix = cv2.getPerspectiveTransform(pts1, pts2) 
        result = cv2.warpPerspective(frame, matrix, (500, 200)) 
    # Wrap the transformed image 
    
        #crop = frame[y1:y3, x1:x3, :]
  
        #cv2.imshow('frame', frame) # Inital Capture 
        #cv2.imshow('frame1', result) # Transformed Capture 
        #cv2.imshow('frame2', frame[]) # Transformed Capture 

        
        self.make_low_res()
        #cv2.namedWindow("Big", cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('Big', 600,400)
        
        print("y1 " + str(y1))
        print("y2 " + str(y1+h))
        print("x1 " + str(x1))
        print("x2 " + str(x1+w))
        cv2.imshow("Big", frame[y1:y1+h, x1:x1+w, :])
        cv2.waitKey(0)
        
    def calc_histogram(img, mask):
        hist_mask = cv2.calcHist([img],[0],mask,[256],[0,256])
        return cv2.minMaxLoc(hist_mask)
