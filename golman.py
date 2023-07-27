import cv2
import numpy as np
from dip import getFinalImage2, loadImage, setupVidCap, showImage, doPerspectiveTransform, findBall
from time import time
from usb_serial import setupSerial, send_pos

old_ball = None
prev_send = time()
prediction = (-1,-1)

if __name__ == "__main__":
    setupSerial(115200, "/dev/ttyACM0")
    
    print("Setting up video camera")
    vidcap = setupVidCap(0)
    print("Camera successfully set up")

    edges = getFinalImage2(vidcap=vidcap)
    raw_img = loadImage(vidcap=vidcap)
    img = doPerspectiveTransform(raw_img, edges)
    ballPos = findBall(img)
    
    old_ball = ballPos
    
    while True:
        raw_img = loadImage(vidcap=vidcap)
        img = doPerspectiveTransform(raw_img, edges)
        ballPos = findBall(img)

        if ballPos == None:
            continue

        # # check if the ball is moving to toward the goal
        if old_ball[0] - ballPos[0] < 0:
            old_ball = ballPos
            continue

        point_1 = ()
        point_2 = ()
        # initial values set to easily determine whether the ball
        # bounced off a wall or not
        # TODO: handle multiple wall bounces / check behaviour when multiple bounces occur or are likely
        point_3 = (-1,-1)
        g=-1
        h=-1
        if old_ball[0] == ballPos[0]:
            # k is infinite
            point_1 = (old_ball[0], 0)
            point_2 = (old_ball[0], 600)
        else:
            k = ((ballPos[1] - old_ball[1]))/((ballPos[0] - old_ball[0]))

            x=799
            y = k * (799 - old_ball[0]) + old_ball[1]
            if y < 0 or y > 600:
                if y < 0:
                    y = 0
                elif y > 600:
                    y = 600
                x = old_ball[0] + (y - old_ball[1]) / k            
            point_1 = (np.round(x).astype(np.uint16),np.round(y).astype(np.uint16))

            x = 0
            y = old_ball[1] - k * old_ball[0]

            if (y>600):
                point_3 = (np.round(0).astype(np.uint16),np.round(1200-y).astype(np.uint16))
    
            if (y<0):
                point_3 = (np.round(0).astype(np.uint16),np.round(-y).astype(np.uint16))

            
            if y < 0 or y > 600:
                if y < 0:
                    y = 0
                elif y > 600:
                    y = 600
                x = old_ball[0] + (y - old_ball[1]) / k

            point_2 = (np.round(x).astype(np.uint16),np.round(y).astype(np.uint16))

        

        # blank = np.zeros((600, 800), dtype=np.uint8)
        cv2.line(img, (0, 200), (0, 400), (255,255,255), 3)

        # cv2.circle(img, old_ball, 5, (255,255,255), 3)
        # cv2.circle(img, ballPos, 10, (255,255,255), 3)
        
        if point_3[0] != -1 and point_3[1] != -1:
            cv2.line(img, point_2, point_3, (255, 255, 0), 2)
            cv2.line(img, point_1, point_2, (255, 255, 0), 2)
        else:
            cv2.line(img, point_1, point_2, (255, 255, 0), 2)

        # if ballPos[0] > 175 and ballPos[0] < 225:
        #     if (point_3[0] == -1):
        #         print(f"{time()} - prediction: {point_2[1] * 55.5 / 600 - 18.5}")
        #     else:
        #         print(f"{time()} - prediction: {point_3[1] * 55.5 / 600 - 18.5}")
        showImage(img, waitKeyTimeout=1)

        delay = 0.05
        
        if point_2[0] == 0 and point_2[1] > 180 and point_2[1] < 420:
            print(int(prediction[1]) - int(point_2[1]))
            if abs(int(prediction[1]) - int(point_2[1])) < 10:
                old_ball = ballPos
                continue
            # print(prediction[1], point_2[1], int(prediction[1]) - int(point_2[1]))

            prediction = point_2

            if time() - prev_send > delay:
                p = f"{600 - point_2[1]}"
                # print(p)
                throw = 0
                if ballPos[0] < 50:
                    throw = 1
                send_pos(p, throw)
                prev_send = time()
        else:
            p = 300
            send_pos(p)
            prev_send = time()

        # waitForArduino(serialPort=sp)
        # print("continuing")


        
        # print(f"p1:{point_1}, p2:{point_2}, p3:{point_3}, ballpos: {ballPos}")
        old_ball = ballPos
