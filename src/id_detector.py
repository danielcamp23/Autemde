import cv2
import numpy as np
from PIL import Image
#from sympy import symbols, Eq, solve

#import matplotlib.pyplot as plt 

xROI = 40;
yROI = 80;
wROI = 560;
hROI = 320;

def draw_roi(in_src_img):
    cv2.rectangle(in_src_img, (xROI, yROI), (xROI + wROI, yROI + hROI), (255, 0, 0), 5)
    

def get_roi_image(in_src_img):
    return in_src_img[yROI:yROI+hROI, xROI:xROI+wROI]
    
def filter_image(in_gray_img):
    #median = cv2.medianBlur(img, 3)
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to grey to reduce detials
    filtered_image = cv2.bilateralFilter(in_gray_img, 10, 17, 17)#Blur to reduce noise
    #second parameter, the higher, the sharpen the image
    return filtered_image

def connect_lines():
    print("jola")

def binaryze_image(img, original_image):
    ret,thresh = cv2.threshold(img,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    canny = cv2.Canny(img, threshold1=(ret*0.3), threshold2=(ret*0.5))
    #cv2.imshow('otr', thresh)
    kernel1 = np.ones((1,10),np.uint8)
    kernel2 = np.ones((10,1),np.uint8)
    #opening1 = cv2.morphologyEx(canny, cv2.MORPH_OPEN, kernel1)
    #opening2 = cv2.morphologyEx(canny, cv2.MORPH_OPEN, kernel2)
    #ret = opening1 | opening2
    
    #kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5,5))
    #opening = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
    #gray = np.float32(img)
    #dst = cv2.cornerHarris(gray,10,3,0.04)
    # Threshold for an optimal value, it may vary depending on the image.
    #img[dst>0.01*dst.max()]=[255]
    
    line_length = 20;
    cv2.imshow('Canny', canny)
    fld = cv2.ximgproc.createFastLineDetector(line_length, _do_merge = True)
    lines = fld.detect(img)
    
    image_width = len(img[0])
    image_height = len(img[1])
    
    width_quarter = image_width / 4
    height_third = image_height / 6
    
    print("hola")
    
    vertical_rhs_lines = []
    vertical_lhs_lines = []
    horizontal_up_lines = []
    horizontal_down_lines = []
    
    for index, line in enumerate(lines) :
        x1 = line[0][0]
        y1 = line[0][1]
        x2 = line[0][2]
        y2 = line[0][3]
        
        color = (0,0,0)
        
        if (abs(x2 - x1) <= 1):
            angle = 90
        else:
            angle = np.arctan(abs(y2 - y1) / abs(x2 - x1)) * 180 / np.pi
        #print(angle)

        vertical_line = angle <= 90 and angle >=84
        horizontal_line = angle >= 0 and angle <= 6
        
        draw = False
        
        if horizontal_line:
                temp_y = max(y1,y2)
                y1 = min(y1,y2)
                y2 = temp_y
                
                temp_x = max(x1,x2)
                x1 = min(x1,x2)
                x2 = temp_x
                
                color = (0,255,0)
                
                
                if (y1 < height_third * 2):
                    # create a mask
                    mask = np.zeros(img.shape, np.uint8)
                    mask[y2.astype(int) : y2.astype(int) + 20, x1.astype(int) : x2.astype(int)] = 255
                    (min_value, max_value, min_idx, max_idx) = calc_histogram(img, mask)
                    horizontal_up_lines.append([x1, y1, x2, y2, max_idx[1]])
                    img[mask > 100] = 0
                    
                elif (y1 > height_third * 3):
                    # create a mask
                    mask = np.zeros(img.shape, np.uint8)
                    mask[y1.astype(int) - 20 : y1.astype(int), x1.astype(int) : x2.astype(int)] = 255
                    (min_value, max_value, min_idx, max_idx) = calc_histogram(img, mask)
                    horizontal_down_lines.append([x1, y1, x2, y2, max_idx[1]])
                    img[mask > 100] = 0
                else:
                    color = (255,0,255)
        elif vertical_line:
                temp_y = max(y1,y2)
                y1 = min(y1,y2)
                y2 = temp_y
                
                temp_x = max(x1,x2)
                x1 = min(x1,x2)
                x2 = temp_x
                
                color = (0,0,255)
                
                if (x1 < width_quarter):
                    # create a mask
                    mask = np.zeros(img.shape, np.uint8)
                    mask[y1.astype(int) : y2.astype(int), x2.astype(int) : x2.astype(int) + 20] = 255
                    (min_value, max_value, min_idx, max_idx) = calc_histogram(img, mask)
                    vertical_lhs_lines.append([x1, y1, x2, y2, max_idx[1]])
                    img[mask > 100] = 0                   
                    
                elif (x1 > width_quarter * 3):
                    # create a mask
                    mask = np.zeros(img.shape, np.uint8)
                    mask[y1.astype(int) : y2.astype(int), x1.astype(int) - 20: x1.astype(int)] = 255
                    (min_value, max_value, min_idx, max_idx) = calc_histogram(img, mask)
                    vertical_rhs_lines.append([x1, y1, x2, y2, max_idx[1]])
                    img[mask > 100] = 0                     
                    color = (25,222,159)
                else:
                    color = (255,255,0)
        
        else:
            continue
                
        cv2.line(original_image, pt1=(x1, y1), pt2=(x2, y2), color=color, thickness=1, lineType=8, shift=0)
        cv2.imshow('Original', original_image)
        #if (draw):
            #plt.plot(hist_mask)
            #plt.show()
            #cv2.waitKey(0)
        #cv2.putText(original_image,str(np.round(angle)), (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
        #print('X: (' + str(x1) + ', ' + str(y1) + ') - ('+ str(x2) + ', ' + str(y2) + ')')
	#a = 0
    
    result_img = fld.drawSegments(img,lines)
    
    sum = 0
    ctr = 1
    mean_val_up = 0
    for (x1, y1, x2, y2, max_value) in horizontal_up_lines:
        mean_val_up += max_value * (x2 - x1)
        ctr += x2 - x1
    mean_val_up /= ctr 
      
    ctr = 1
    mean_val_down = 0
    for (x1, y1, x2, y2, max_value) in horizontal_down_lines:
        mean_val_down += max_value * (x2 - x1)
        ctr += x2 - x1
    mean_val_down /= ctr
    
    ctr = 1
    mean_val_lhs = 0
    for (x1, y1, x2, y2, max_value) in vertical_lhs_lines:
        mean_val_lhs += max_value * (y2 - y1)
        ctr += y2 - y1
    mean_val_lhs /= ctr
        
    ctr = 1
    mean_val_rhs = 0
    for (x1, y1, x2, y2, max_value) in vertical_rhs_lines:
        mean_val_rhs += max_value * (y2 - y1)
        ctr += y2 - y1
    mean_val_rhs /= ctr    
   
    
    h_up_index = 0
    h_down_index = 0
    v_lhs_index = 0
    v_rhs_index = 0
    
    candidate = 0
    for index, (x1, y1, x2, y2, max_val) in enumerate(horizontal_up_lines):
        if index == 0:
            candidate = max_val
        if (abs(max_val - mean_val_up) <= abs(candidate - mean_val_up)):
            candidate = max_val
            h_up_index = index
    print("UP: " + str(candidate))
    
    candidate = 0
    for index, (x1, y1, x2, y2, max_val) in enumerate(horizontal_down_lines):
        if index == 0:
            candidate = max_val
        if (abs(max_val - mean_val_down) <= abs(candidate - mean_val_down)):
            candidate = max_val
            h_down_index = index
    print("Down: " + str(candidate))
    
    candidate = 0
    for index, (x1, y1, x2, y2, max_val) in enumerate(vertical_lhs_lines):
        if index == 0:
            candidate = max_val           
        if (abs(max_val - mean_val_lhs) <= abs(candidate - mean_val_lhs)):
            candidate = max_val
            v_lhs_index = index
    #print("LF: " + str(candidate))
    
    candidate = 0
    for index, (x1, y1, x2, y2, max_val) in enumerate(vertical_rhs_lines):
        if index == 0:
            candidate = max_val            
        if (abs(max_val - mean_val_rhs) <= abs(candidate - mean_val_rhs)):
            candidate = max_val
            v_rhs_index = index            
    #print("RI: " + str(candidate))
    
    if vertical_lhs_lines and horizontal_up_lines:
        cv2.circle(img,(vertical_lhs_lines[v_lhs_index][0], horizontal_up_lines[h_up_index][1]), 10, (255,0,0), 3)
     
    if v_lhs_index and horizontal_down_lines:
        cv2.circle(img,(vertical_lhs_lines[v_lhs_index][0], horizontal_down_lines[h_down_index][1]), 10, (255,0,0), 3)
        
    if vertical_rhs_lines and horizontal_up_lines:
        cv2.circle(img,(vertical_rhs_lines[v_rhs_index][0], horizontal_up_lines[h_up_index][1]), 10, (255,0,0), 3)
    
    if vertical_rhs_lines and horizontal_down_lines:
        cv2.circle(img,(vertical_rhs_lines[v_rhs_index][0], horizontal_down_lines[h_down_index][1]), 10, (255,0,0), 3)
    
    cv2.imshow('otr', img)
    
    return result_img
    #return canny
   

def calc_histogram(img, mask):
    hist_mask = cv2.calcHist([img],[0],mask,[256],[0,256])
    return cv2.minMaxLoc(hist_mask)
    
def hough_lines(img, original_image):
    ret,thresh = cv2.threshold(img,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    canny = cv2.Canny(img, threshold1=(ret*0.3), threshold2=(ret*0.5))
    #canny = cv2.Canny(img, threshold1=100, threshold2=150)
    cv2.imshow('Canny', canny)
    
    rho = 4  # distance resolution in pixels of the Hough grid
    theta = np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 10  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 200  # minimum number of pixels making up a line
    max_line_gap = 10  # maximum gap in pixels between connectable line segments

    #lines = cv2.HoughLines(canny,rho,theta,threshold)
    lines = cv2.HoughLinesP(canny, rho, theta, threshold, np.array([]), min_line_length, max_line_gap);
    
    image_width = len(img[0])
    image_height = len(img[1])
    
    print("W: " + str(image_width))
    print("H: " + str(image_height))
      
    '''
    for line in lines:
        print("LINEEEE -" + str(line.shape))
        for rho,theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))

            cv2.line(original_image,(x1,y1),(x2,y2),(0,0,255),2)
            cv2.imshow('ORI', original_image)
            if cv2.waitKey(0) & 0xFF == 27:
                break
    '''
    for line in lines:
        print("LINEEEE")
        for x1,y1,x2,y2 in line:
            print("x1: " + str(x1))
            print("y1: " + str(y1))
            print("y1: " + str(x1))
            print("y2: " + str(y2))
            cv2.line(original_image,(x1,y1),(x2,y2),(0,0,255),2)
            #cv2.waitKey(0)

    
def cluster_image(img):
    Z = img.reshape((-1,3))
    Z = np.float32(Z)
 
    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 2
    ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

     # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))
 
    fld = cv2.ximgproc.createFastLineDetector()
    lines = fld.detect(img)

    result_img = fld.drawSegments(img,lines)
    
    cv2.imshow('Cluster',result_img)
    
#def focus_image(in_img):
    
i = 0;
cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
#v2.resizeWindow('Original', 400,400)

#cv2.namedWindow("Filtered", cv2.WINDOW_NORMAL)
#cv2.resizeWindow('Filtered', 200,200)

#cv2.namedWindow("Binary", cv2.WINDOW_NORMAL)
#cv2.resizeWindow('Binary', 200,200)

#cv2.namedWindow("Cluster", cv2.WINDOW_NORMAL)
#cv2.resizeWindow('Cluster', 200,200)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,1024);
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,768);

width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float



while True:
    #path = './cedulas/cc_' + str(i) + '.jpg'
    i += 1
    
    ret, original_image = cap.read()
    draw_roi(original_image)
    
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    roi_image = get_roi_image(gray_image)
    filtered_image = filter_image(roi_image)
    
    #original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    

    #original_image = cv2.imread(path)
    #
    binary_image = binaryze_image(filtered_image, original_image)
	#cluster_image(filtered_image)
    #hough_lines(filtered_image, original_image)
    
    cv2.imshow('Original', original_image)
    cv2.imshow('Filtered', filtered_image)
    cv2.imshow('Binary', binary_image)
	
	
    key = cv2.waitKey(20) & 0xFF
    if (key == 27):
        break
	
cap.release()
cv2.destroyAllWindows()
