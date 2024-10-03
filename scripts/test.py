from RemoteCams import RemoteCams
import time
import cv2
import numpy as np


def find_dot(img):
    # img = cv.GaussianBlur(img,(5,5),0)
    grey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    grey = cv2.threshold(grey, 255*0.2, 255, cv2.THRESH_BINARY)[1]
    contours,_ = cv2.findContours(grey, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.drawContours(img, contours, -1, (0,255,0), 1)

    image_points = []
    for contour in contours:
        moments = cv2.moments(contour)
        if moments["m00"] != 0:
            center_x = int(moments["m10"] / moments["m00"])
            center_y = int(moments["m01"] / moments["m00"])
            cv2.putText(img, f'({center_x}, {center_y})', (center_x,center_y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (100,255,100), 1)
            cv2.circle(img, (center_x,center_y), 1, (100,255,100), -1)
            image_points.append([center_x, center_y])

    if len(image_points) == 0:
        image_points = [[None, None]]

    return img, image_points[0]

def get_point(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Use minMaxLoc to find the brightest point in the grayscale image
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

        # Draw a circle around the brightest point
    cv2.circle(image, maxLoc, 10, (0, 0, 255), 2)

    # Print the coordinates of the brightest point
    # print("Coordinates of the brightest point:", maxLoc)

    return maxLoc

font = cv2.FONT_HERSHEY_SIMPLEX

prev_frame_time = 0
# used to record the time at which we processed current frame 
new_frame_time = 0

cam = RemoteCams(["192.168.146.253","192.168.146.85","192.168.146.41"], 8005)

time.sleep(5)

while True:
    
    img = cam.get_frames()

    new_frame_time = time.time() 

    fps = 1/(new_frame_time-prev_frame_time) 
    prev_frame_time = new_frame_time 
  
    # converting the fps into integer 
    fps = int(fps) 
    # get_point(img[0])
    # get_point(img[1])
    # get_point(img[2])
    # converting the fps to string so that we can display it on frame 
    # by using putText function 
    
    fps = str(fps)
    cv2.putText(img[0], fps, (7, 70), font , 3, (100, 255, 0), 3, cv2.LINE_AA)
    
    cv2.imshow("test",np.hstack(((img[0],img[1],img[2]))))
    
    k = cv2.waitKey(5)
    if k ==ord('q'):
        break
    
cam.kill_all()