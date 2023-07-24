import cv2
import numpy as np
from dip import getFinalImage, loadImage, setupVidCap, showImage, doPerspectiveTransform
# from arduino import setupSerial, sendToArduino, waitForArduino
from time import sleep, time
# import os
from usb_serial import setupSerial, send_pos

old_ball = None
prev_send = time()

def getBallPosition(image: cv2.Mat):
    contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    c = max(contours, key=cv2.contourArea)    
    x, y, w, h = cv2.boundingRect(c)
    
    return ((x+x+w)//2,(y+y+h)//2)


def binarization(image: cv2.Mat):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binarized = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    return binarized
    
    # element = cv2.getStructuringElement(cv2.MORPH_RECT, ksize=kernel_size, anchor=anchor_size)
    # eroded = cv2.erode(binarized, element)


if __name__ == "__main__":
    # serialPort = "COM3"
    # print(f"Connecting to arduino on port {serialPort}")
    # sp = setupSerial(115200, serialPortName=serialPort)
    # print("Connected to arduino!")
    # sleep(3)
    # print("Continuing")
    setupSerial(115200, "/dev/ttyACM0")
    
    print("Setting up video camera")
    vidcap = setupVidCap(2)
    print("Camera successfully set up")
    edges = getFinalImage(vidcap=vidcap)
    
    raw_img = loadImage(vidcap=vidcap)
    
    img = doPerspectiveTransform(raw_img, edges)
    binarized = binarization(img)
    ballPos = getBallPosition(binarized)
    
    old_ball = ballPos
    
    while True:
        raw_img = loadImage(vidcap=vidcap)
    
        img = doPerspectiveTransform(raw_img, edges)
        binarized = binarization(img)
        ballPos = getBallPosition(binarized)
        
        # # check if the ball is moving to toward the goal
        if old_ball[0] - ballPos[0] < 0:
            # print(old_ball, ballPos)
            # print("the ball is moving away from the goal!")
            old_ball = ballPos
            continue

        point_1 = ()
        point_2 = ()
        # initial values set to easily determine whether the ball
        # bounced off a wall or not
        # TODO: handle multiple wall bounces / check behaviour when multiple bounces occur or are likely
        point_3 = (-1,-1)

        if old_ball[0] == ballPos[0]:
            # k is infinite
            point_1 = (old_ball[0], 0)
            point_2 = (old_ball[0], 600)
        else:
            k = ((ballPos[1] - old_ball[1]))/((ballPos[0] - old_ball[0]))

            # find y coordinate at x=0
            x = 0
            y = old_ball[1] - k * old_ball[0]

            # handle out of bounds
            if y < 0 or y > 600:
                if y < 0:
                    y = 0
                elif y > 600:
                    y = 600
                x = old_ball[0] + (y - old_ball[1]) / k
            
            point_1 = (np.round(x).astype(np.uint16),np.round(y).astype(np.uint16))

            # find y coordinate at x=799
            x = 799
            y = k * (799 - old_ball[0]) + old_ball[1]

            # handle out of bounds
            if y < 0 or y > 600:
                if y < 0:
                    y = 0
                elif y > 600:
                    y = 600
                x = old_ball[0] + (y - old_ball[1]) / k

            point_2 = (np.round(x).astype(np.uint16),np.round(y).astype(np.uint16))

            # check for collision and calculate
            # ball direction after collision
            # TODO: get rid of magic numbers
            if point_2[0] < 799:
                x = 799
                B = 600
                if k < 0:
                    B = 0
                
                n = 2 * B - point_2[1] + k * point_2[0]
                y = -k * x + n

                # handle out of bounds
                if y < 0 or y > 600:
                    if y < 0:
                        y = 0
                    elif y > 600:
                        y = 600
                    x = (n - y) / k

                point_3 = (np.round(x).astype(np.uint16),np.round(y).astype(np.uint16))
        

        # blank = np.zeros((600, 800), dtype=np.uint8)
        cv2.line(img, (0, 200), (0, 400), (255,255,255), 3)

        cv2.circle(img, old_ball, 5, (255,255,255), 3)
        cv2.circle(img, ballPos, 10, (255,255,255), 3)
        cv2.line(img, point_1, point_2, (255, 255, 0), 2)
        
        if point_3[0] != -1 and point_3[1] != -1:
            cv2.line(img, point_2, point_3, (255, 255, 0), 2)

        # if point_1[0] == 0 and point_1[1] > 200 and point_1[1] < 400:
        if ballPos[1] > 200 and ballPos[1] < 410:
            # os.system("play -nq -t alsa synth 0.3 sine 1000")
            # print("goal is likely!")
            # if time() - prevTime > 0.5:
            #     print(f"sent to arduino: {point_1[1]} 0")
            #     sendToArduino(serialPort=sp, stringToSend=f"{point_1[1]} 0")
            #     prevTime = time()
            # send_pos(point_1[1])
            delay = 0.05
        # print(f"new position in {(delay - (time.time() - prev_send)) * 100}...")
            if time() - prev_send > delay:
                # p = point_1[1]
                p = 600 - ballPos[1]
                send_pos(p)
                # print(f"{19*(p-200)/200}cm")
                prev_send = time()

        # waitForArduino(serialPort=sp)
        # print("continuing")

        showImage(blank, waitKeyTimeout=1)

        
        print(f"p1:{point_1}, p2:{point_2}, p3:{point_3}, ballpos: {ballPos}")
        old_ball = ballPos
