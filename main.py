import cv2
import os
import numpy as np
from dip import getFinalImage

images = []

# load images
# TODO: modify to enable reading the images from a live USB camera feed
for image in os.listdir("./data/"):
    images.append(cv2.imread("./data/" + image))

balls = []

# locate the ball in each image and append its center coordinates to the list
for image in images:
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # TODO: find appropriate mask for real-world ball
    mask = cv2.inRange(hsv_image, np.array([0, 0, 0]), np.array([0, 0, 0]))

    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    c = max(contours, key=cv2.contourArea)

    x, y, w, h = cv2.boundingRect(c)

    center = (np.round((x+x+w)/2).astype(np.uint16),np.round((y+y+h)/2).astype(np.uint16))

    balls.append(center)

print(balls)

# write the equation for ball trajectory estimation
# y - y1 = ((y2-y1)/(x2-x1)) * (x - x1)

# TODO: change into a 'while True' loop with try catch block to stop execution with Ctrl-C
for i in range(1, len(balls)):
    print(f"ball number: {i}, old ball: {balls[i-1]}, new ball: {balls[i]}")

    # check if the ball is moving to toward the goal (on the right)
    if balls[i-1][0].astype(np.int16) - balls[i][0].astype(np.int16) >= 0:
        print("the ball is moving to the left!")

        blank = np.zeros((600,800), dtype=np.uint8)

        cv2.putText(blank, f"ball number {i} is moving to the left", (20,300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)

        cv2.imshow("left", blank)
        cv2.waitKey(0)

        continue

    point_1 = ()
    point_2 = ()
    # initial values set to easily determine whether the ball
    # bounced off a wall or not
    # TODO: handle multiple wall bounces / check behaviour when multiple bounces occur or are likely
    point_3 = (-1,-1)

    if balls[i-1][0] == balls[i][0]:
        # k is infinite
        point_1 = (x, 0)
        point_2 = (x, 600)
    else:
        k = ((balls[i][1] - balls[i-1][1]).astype(np.int16))/((balls[i][0] - balls[i-1][0]).astype(np.int16))

        # find y coordinate at x=0
        x = 0
        y = balls[i-1][1] - k * balls[i-1][0]

        # handle out of bounds
        if y < 0 or y > 600:
            if y < 0:
                y = 0
            elif y > 600:
                y = 600
            x = balls[i-1][0] + (y - balls[i-1][1]) / k
        
        point_1 = (np.round(x).astype(np.uint16),np.round(y).astype(np.uint16))

        # find y coordinate at x=799
        x = 799
        y = k * (799 - balls[i-1][0]) + balls[i-1][1]

        # handle out of bounds
        if y < 0 or y > 600:
            if y < 0:
                y = 0
            elif y > 600:
                y = 600
            x = balls[i-1][0] + (y - balls[i-1][1]) / k

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

    cv2.circle(blank, balls[i-1], 5, (255,255,255), 3)
    cv2.circle(blank, balls[i], 10, (255,255,255), 3)
    cv2.line(blank, point_1, point_2, (255, 255, 0), 2)
    
    if point_3[0] != -1 and point_3[1] != -1:
        cv2.line(blank, point_2, point_3, (255, 255, 0), 2)

    if point_2[0] == 799 and point_2[1] > 100 and point_2[1] < 500:
        print("goal is likely!")

    cv2.imshow("circles with line and prediction", blank)
    cv2.waitKey(0)
