# import necessary libraries

import cv2
import numpy as np

vidcap = cv2.VideoCapture(2)
vidcap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920.0)
vidcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080.0)

# while True:
# image = cv2.imread("Photo-2.jpeg")

ret, image = vidcap.read()
vidcap.release()
# cv2.imshow("raw",image)
# cv2.waitKey(0)

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

