# import necessary libraries
import cv2
import numpy as np
import colorsys


def setupVidCap():
    vidcap = cv2.VideoCapture(2)
    vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920.0)
    vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080.0)
    return vidcap


def loadImage(vidcap):
    _, image = vidcap.read()
    return image

# vidcap.release()

# cv2.imshow("", image)
# cv2.waitKey(0)

upperBound = colorsys.rgb_to_hsv(255,190,170) # hsv(14, 33%, 100%)
lowerBound = colorsys.rgb_to_hsv(255,160,150) # hsv(6, 41%, 100%)

hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
# mask = cv2.inRange(hsv_image, lowerBound, upperBound)

max_value = 255
max_value_H = 360
low_H = 0
low_S = 79
low_V = 255
high_H = 9
high_S = 90
high_V = 255

uglovi = 0
konture = None

while uglovi != 4:
    try:
        mask = cv2.inRange(hsv_image, (low_H, low_S, low_V), (high_H, high_S, high_V))
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10), (4, 4))
        dilatation_dst = cv2.dilate(mask, element)
        # cv2.imshow("Lol", dilatation_dst)
        # cv2.waitKey(0)
        # print(len(contours))
        contours, _ = cv2.findContours(dilatation_dst, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        uglovi = len(contours)
        print(f"treuntno: {uglovi}")
        konture = contours
    except KeyboardInterrupt:
        break

c = max(contours, key=cv2.contourArea)
print(f"konacno: {len(konture)}")
x, y, w, h = cv2.boundingRect(c)

# center = (np.round((x+x+w)/2).astype(np.uint16),np.round((y+y+h)/2).astype(np.uint16))

coords = np.float32([[704,711],[821,63],[377,8],[111,548]])
output = np.float32([[800,0],[0,0],[0,600],[800,600]])
perspective_transform = cv2.getPerspectiveTransform(coords, output)

# pts = np.float32(np.array([[[800,600]]]))

# M = cv2.perspectiveTransform(pts, perspective_transform, )
# print(M)

# dst = cv2.warpPerspective(image, M, (800,600))

dst = cv2.warpPerspective(image, perspective_transform, (800,600))

cv2.imshow("output", dst)
cv2.waitKey(0)

if __name__ == "__main__":
    pass
