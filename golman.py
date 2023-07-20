import cv2
import numpy as np
from dip import getFinalImage, loadImage, setupVidCap, showImage, doPerspectiveTransform
from time import sleep

old_ball = None


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
    vidcap = setupVidCap(1)
    edges = getFinalImage(vidcap=vidcap)
    
    raw_img = loadImage(vidcap=vidcap)
    
    img = doPerspectiveTransform(raw_img, edges)
    binarized = binarization(img)
    ballPos = getBallPosition(binarized)
    
    old_ball = ballPos
    
    while True:
        sleep(0.1)
        
        raw_img = loadImage(vidcap=vidcap)
    
        img = doPerspectiveTransform(raw_img, edges)
        binarized = binarization(img)
        ballPos = getBallPosition(binarized)
        
        # showImage(binarized)
        
        print(old_ball, ballPos)
        
        # # print(f"ball number: {i}, old ball: {old_ball}, new ball: {ballPos}")

        # # check if the ball is moving to toward the goal
        print(old_ball[0] - ballPos[0])
        if old_ball[0] - ballPos[0] < 0:
            # print(old_ball, ballPos)
            print("the ball is moving away from the goal!")
            old_ball = ballPos
            continue

        point_1 = ()
        point_2 = ()
        # # initial values set to easily determine whether the ball
        # # bounced off a wall or not
        # # TODO: handle multiple wall bounces / check behaviour when multiple bounces occur or are likely
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

        blank = np.zeros((600, 800), dtype=np.uint8)
        cv2.line(blank, (799, 100), (799, 500), (255,255,255), 3)

        cv2.circle(blank, old_ball, 5, (255,255,255), 3)
        cv2.circle(blank, ballPos, 10, (255,255,255), 3)
        cv2.line(blank, point_1, point_2, (255, 255, 0), 2)
        
        if point_3[0] != -1 and point_3[1] != -1:
            cv2.line(blank, point_2, point_3, (255, 255, 0), 2)

        if point_2[0] == 799 and point_2[1] > 100 and point_2[1] < 500:
            print("goal is likely!")

        showImage(blank)
        
        print(point_1, point_2, point_3)
        old_ball = ballPos
